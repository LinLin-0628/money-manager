from pathlib import Path

from app.core.logging import LOG_FILE_JSON, LOG_FILE_TEXT


def clear_log_file(file_path: Path) -> None:
    """Safely clear the content of a log file."""
    try:
        file_path.write_text("")
        print(f"Cleared: {file_path}")  # noqa: T201
    except Exception as e:
        print(f"Failed to clear {file_path}: {e}")  # noqa: T201


def main() -> None:
    clear_log_file(LOG_FILE_TEXT)
    clear_log_file(LOG_FILE_JSON)


if __name__ == "__main__":
    main()
