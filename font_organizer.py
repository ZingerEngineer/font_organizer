"""Font Organizer — entry point."""

from cli import parse_args
from organizer import run


def main() -> None:
    config = parse_args()
    run(config)


if __name__ == "__main__":
    main()
