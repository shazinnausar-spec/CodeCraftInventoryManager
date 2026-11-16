# Import application directory setup.
from app.config import create_app_directories

# Import database initialization.
from app.database import initialize_database

# Import the main application window.
from app.ui.main_window import MainWindow


def main():

    # Create required application directories.
    create_app_directories()

    # Initialize the SQLite database.
    initialize_database()

    # Create the main application window.
    app = MainWindow()

    # Start the application.
    app.mainloop()


if __name__ == "__main__":

    main()