from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from services.database_service import get_database_path, initialize_database


def main() -> None:
    initialize_database()

    print("Database initialized successfully.")
    print(f"Database path: {get_database_path()}")


if __name__ == "__main__":
    main()