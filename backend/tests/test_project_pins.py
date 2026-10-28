"""The uv project pins the stack.md versions and locks them."""

import sys
import tomllib
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]

RUNTIME_PINS = {
    "alembic": "~=1.20.1",
    "argon2-cffi": "~=25.1.0",
    "email-validator": "~=2.3.0",
    "fastapi": "~=0.162.0",
    "psycopg[binary]": "~=3.3.6",
    "pydantic": "~=2.14.1",
    "pydantic-settings": "~=2.16.1",
    "pyjwt": "~=2.15.1",
    "sqlalchemy": "~=2.1.6",
    "uvicorn[standard]": "~=0.54.0",
}

DEV_PINS = {
    "httpx2": "~=2.16.0",
    "mypy": "~=2.4.0",
    "pytest": "~=9.2.0",
    "ruff": "~=0.17.3",
}


def _compatible(pin: str, version: str) -> bool:
    """True when ``version`` satisfies a ``~=`` pin. 0.x treats minor as breaking."""

    assert pin.startswith("~=")
    base = pin.removeprefix("~=")
    parts = base.split(".")
    version_parts = version.split(".")
    if parts[0] == "0":
        prefix = ".".join(parts[:2])
        return version_parts[0] == "0" and ".".join(version_parts[:2]) == prefix
    prefix = ".".join(parts[:2])
    return ".".join(version_parts[:2]) == prefix and version >= base


def test_runtime_is_python_314() -> None:
    assert sys.version_info[:2] == (3, 14)
    assert sys.version_info >= (3, 14, 10)


def test_python_and_dependency_pins() -> None:
    document = tomllib.loads((BACKEND_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = document["project"]
    assert project["requires-python"] == ">=3.14.10,<3.15"
    assert set(project["dependencies"]) == {f"{name}{pin}" for name, pin in RUNTIME_PINS.items()}
    assert set(document["dependency-groups"]["dev"]) == {
        f"{name}{pin}" for name, pin in DEV_PINS.items()
    }
    assert (BACKEND_ROOT / ".python-version").read_text(encoding="utf-8").strip() == "3.14.10"


def test_lock_file_matches_pins() -> None:
    lock_path = BACKEND_ROOT / "uv.lock"
    assert lock_path.is_file()
    lock = tomllib.loads(lock_path.read_text(encoding="utf-8"))
    locked = {package["name"]: package["version"] for package in lock["package"]}
    expected = {**RUNTIME_PINS, **DEV_PINS}
    for requirement, pin in expected.items():
        name = requirement.split("[", 1)[0]
        assert name in locked, name
        assert _compatible(pin, locked[name]), f"{name} {locked[name]} does not match {pin}"
