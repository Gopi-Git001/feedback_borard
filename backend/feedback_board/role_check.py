"""Refuse to serve when DATABASE_URL is not the restricted application role.

Runs from the ASGI lifespan, which uvicorn executes before it opens the port.
There is no setting that turns the check off. Failure messages name the reason
only: never a URL, a password, or a traceback from the driver.
"""

import os
from urllib.parse import urlsplit

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

_ROLE_SQL = text(
    """
    SELECT
        current_user AS role_name,
        r.rolsuper AS is_superuser,
        r.rolbypassrls AS bypasses_rls,
        pg_get_userbyid(d.datdba) AS database_owner
    FROM pg_roles AS r
    CROSS JOIN pg_database AS d
    WHERE r.rolname = current_user
      AND d.datname = current_database()
    """,
)

# The compose owner is also the migration role (DATABASE_MIGRATION_URL).
_OWNER_ROLE_NAME = "feedback_owner"


class StartupRefused(RuntimeError):
    """The process must not serve. The message never includes a URL or password."""


def assert_runtime_role(engine: Engine) -> None:
    migration_role = _migration_role_name()
    try:
        with engine.connect() as connection:
            row = connection.execute(_ROLE_SQL).one()
    except SQLAlchemyError, OSError:
        raise StartupRefused(
            "startup refused: database role check could not be completed",
        ) from None

    role_name = str(row.role_name)
    if bool(row.is_superuser):
        raise StartupRefused("startup refused: database role is a superuser")
    if bool(row.bypasses_rls):
        raise StartupRefused("startup refused: database role has BYPASSRLS")
    if role_name == str(row.database_owner) or role_name == _OWNER_ROLE_NAME:
        raise StartupRefused("startup refused: database role is the owner role")
    if migration_role is not None and role_name == migration_role:
        raise StartupRefused("startup refused: database role is the migration role")


def _migration_role_name() -> str | None:
    """Username of DATABASE_MIGRATION_URL, if that variable is set.

    The value is never logged. A present but unusable value fails closed.
    When the variable is unset, the database-owner check still rejects the
    role Alembic uses in this project.
    """

    raw = os.environ.get("DATABASE_MIGRATION_URL", "")
    if raw == "":
        return None
    try:
        username = urlsplit(raw).username
    except ValueError:
        raise StartupRefused(
            "startup refused: database role check could not be completed",
        ) from None
    if username is None or username == "":
        raise StartupRefused(
            "startup refused: database role check could not be completed",
        )
    return username
