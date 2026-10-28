#!/bin/sh
# TASK-003: take the app role's access to Alembic's bookkeeping table away.
#
# Alembic runs only as the owner role. The default privileges set by
# db/init/01-roles.sh grant SELECT/INSERT/UPDATE/DELETE on every table the owner
# creates, including public.alembic_version, so this REVOKE must run right after
# the migration that creates that table (TASK-006 must call it right after the
# first migration, in the migration runner, and again after any step that drops
# and recreates the table). Safe to run at any time and any number of times: if
# the table does not exist yet it does nothing.
#
# Run it on the live db (manual helper, not run automatically):
#   docker compose exec db sh /opt/db-ops/revoke-app-on-alembic-version.sh
#
# Equivalent SQL, as the owner:
#   REVOKE ALL ON TABLE public.alembic_version FROM <APP_DB_USER>;
set -eu

: "${POSTGRES_USER:?POSTGRES_USER is not set}"
: "${POSTGRES_DB:?POSTGRES_DB is not set}"
: "${APP_DB_USER:?APP_DB_USER is not set}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv app_user APP_DB_USER

SELECT to_regclass('public.alembic_version') IS NOT NULL AS has_table \gset
\if :has_table
  REVOKE ALL ON TABLE public.alembic_version FROM :"app_user";
  \echo 'revoked all privileges of' :app_user 'on public.alembic_version'
\else
  \echo 'public.alembic_version does not exist yet: nothing to revoke (run again after the first migration)'
\endif
SQL
