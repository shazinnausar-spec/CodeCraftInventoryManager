# Import the os module to access Windows environment variables.
import os

# Import Path to work with folders and files safely.
from pathlib import Path


# Application information.
APP_NAME = "CodeCraft Inventory Manager"
APP_VERSION = "1.0.0"
APP_AUTHOR = "CodeCraft Studio"


# Get the Windows Local AppData directory.
# This keeps application data outside the project directory.
LOCAL_APP_DATA = Path(
    os.getenv(
        "LOCALAPPDATA",
        str(Path.home() / "AppData" / "Local")
    )
)


# Main application data directory.
APP_DATA_DIR = (
    LOCAL_APP_DATA
    / "CodeCraftStudio"
    / "CodeCraftInventoryManager"
)


# Database directory and database file.
DATABASE_DIR = APP_DATA_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "inventory.db"


# Backup directory.
BACKUP_DIR = APP_DATA_DIR / "backups"


# Export directory.
EXPORT_DIR = APP_DATA_DIR / "exports"


# Create required directories if they do not already exist.
def create_app_directories():

    # Create the main application data directory.
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create the database directory.
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    # Create the backup directory.
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Create the export directory.
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)