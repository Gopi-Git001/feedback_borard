"""Process entrypoint. Invalid configuration exits non-zero before serving."""

import sys

import uvicorn

from feedback_board.app import create_app
from feedback_board.logging_config import configure_logging, log_relaxations
from feedback_board.settings import SettingsError, load_settings


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    try:
        settings = load_settings()
    except SettingsError as exc:
        print(f"startup refused: {exc}", file=sys.stderr)
        raise SystemExit(1) from None

    configure_logging(settings)
    log_relaxations(settings)
    if args == ["--check"]:
        raise SystemExit(0)
    if args:
        print("usage: python -m feedback_board.main [--check]", file=sys.stderr)
        raise SystemExit(2) from None

    # ADR-002: the application parses forwarded headers itself, so uvicorn must not.
    # Bind is loopback until TASK-007 runs this process inside the backend container.
    uvicorn.run(
        create_app(settings),
        host="127.0.0.1",
        port=8000,
        proxy_headers=False,
        forwarded_allow_ips="",
    )


if __name__ == "__main__":
    main()
