
# Import operating system utilities.
import os

# Import CustomTkinter.
import customtkinter as ctk

# Import message boxes.
from tkinter import messagebox

# Import application configuration.
from app.config import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR,
    APP_DATA_DIR,
    DATABASE_DIR,
    DATABASE_PATH,
    BACKUP_DIR,
    EXPORT_DIR,
    create_app_directories
)

# Import database functions.
from app.database import (
    check_database_connection,
    get_database_info
)

# Import theme settings.
from app.ui.theme import (
    COLORS,
    FONT_FAMILY
)


class SettingsPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        # Configure page layout.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Store database status labels.
        self.status_label = None
        self.version_label = None
        self.tables_label = None

        # Build page sections.
        self.create_heading()
        self.create_content()

        # Load current application information.
        self.refresh_settings()

    def create_heading(self):

        heading = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        heading.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(25, 15)
        )

        title = ctk.CTkLabel(
            heading,
            text="Settings",
            font=(FONT_FAMILY, 25, "bold"),
            text_color=COLORS["text"]
        )

        title.pack(anchor="w")

        description = ctk.CTkLabel(
            heading,
            text="View application information and manage local storage locations.",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"]
        )

        description.pack(
            anchor="w",
            pady=(5, 0)
        )

    def create_content(self):

        # Create a scrollable content area.
        self.content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        self.content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )

        self.content.grid_columnconfigure(
            0,
            weight=1
        )

        self.create_database_section()
        self.create_storage_section()
        self.create_application_section()

    def create_section_card(self, title, description):

        card = ctk.CTkFrame(
            self.content,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        card.pack(
            fill="x",
            pady=(0, 15)
        )

        heading = ctk.CTkLabel(
            card,
            text=title,
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"]
        )

        heading.pack(
            anchor="w",
            padx=20,
            pady=(18, 4)
        )

        subtitle = ctk.CTkLabel(
            card,
            text=description,
            font=(FONT_FAMILY, 11),
            text_color=COLORS["secondary_text"]
        )

        subtitle.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        return card

    def create_database_section(self):

        card = self.create_section_card(
            "Database Information",
            "Check the connection and view database details."
        )

        self.status_label = ctk.CTkLabel(
            card,
            text="Checking database...",
            font=(FONT_FAMILY, 13, "bold"),
            text_color=COLORS["secondary_text"]
        )

        self.status_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 10)
        )

        self.version_label = ctk.CTkLabel(
            card,
            text="SQLite version: Checking...",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["secondary_text"]
        )

        self.version_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        self.tables_label = ctk.CTkLabel(
            card,
            text="Database tables: Checking...",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["secondary_text"],
            wraplength=850,
            justify="left"
        )

        self.tables_label.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        refresh_button = ctk.CTkButton(
            card,
            text="Refresh Database Status",
            width=190,
            height=35,
            font=(FONT_FAMILY, 11),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.refresh_settings
        )

        refresh_button.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

    def create_storage_section(self):

        card = self.create_section_card(
            "Storage Locations",
            "Your application data is stored locally on this computer."
        )

        self.create_location_row(
            card,
            "Application Data",
            APP_DATA_DIR,
            "Open Folder"
        )

        self.create_location_row(
            card,
            "Database Folder",
            DATABASE_DIR,
            "Open Folder"
        )

        self.create_location_row(
            card,
            "Database File",
            DATABASE_PATH,
            "Open Folder"
        )

        self.create_location_row(
            card,
            "Backup Folder",
            BACKUP_DIR,
            "Open Folder"
        )

        self.create_location_row(
            card,
            "Export Folder",
            EXPORT_DIR,
            "Open Folder"
        )

    def create_location_row(
        self,
        parent,
        title,
        location,
        button_text
    ):

        row = ctk.CTkFrame(
            parent,
            fg_color="#F8FAFC",
            corner_radius=8
        )

        row.pack(
            fill="x",
            padx=15,
            pady=5
        )

        row.grid_columnconfigure(
            0,
            weight=1
        )

        name_label = ctk.CTkLabel(
            row,
            text=title,
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"]
        )

        name_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=12,
            pady=(9, 2)
        )

        path_label = ctk.CTkLabel(
            row,
            text=str(location),
            font=(FONT_FAMILY, 10),
            text_color=COLORS["secondary_text"],
            anchor="w",
            justify="left",
            wraplength=750
        )

        path_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 9)
        )

        button = ctk.CTkButton(
            row,
            text=button_text,
            width=105,
            height=32,
            font=(FONT_FAMILY, 10),
            fg_color=COLORS["border"],
            hover_color="#CBD5E1",
            text_color=COLORS["text"],
            command=lambda path=location: self.open_location(path)
        )

        button.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=12
        )

    def create_application_section(self):

        card = self.create_section_card(
            "Application Information",
            "Information about this application."
        )

        information = [
            ("Application Name", APP_NAME),
            ("Version", APP_VERSION),
            ("Developer", APP_AUTHOR),
            ("Database Engine", "SQLite"),
            ("Interface Framework", "CustomTkinter"),
            ("Programming Language", "Python")
        ]

        for label_text, value_text in information:

            row = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                padx=20,
                pady=5
            )

            label = ctk.CTkLabel(
                row,
                text=label_text,
                font=(FONT_FAMILY, 11),
                text_color=COLORS["secondary_text"]
            )

            label.pack(side="left")

            value = ctk.CTkLabel(
                row,
                text=value_text,
                font=(FONT_FAMILY, 11, "bold"),
                text_color=COLORS["text"]
            )

            value.pack(side="right")

        # Add bottom spacing.
        ctk.CTkFrame(
            card,
            height=10,
            fg_color="transparent"
        ).pack()

    def refresh_settings(self):

        try:

            # Check the database connection.
            connected = check_database_connection(
                DATABASE_PATH
            )

            if connected:

                self.status_label.configure(
                    text="● Database Connected",
                    text_color=COLORS["success"]
                )

                # Retrieve database information.
                database_info = get_database_info(
                    DATABASE_PATH
                )

                self.version_label.configure(
                    text=(
                        "SQLite version: "
                        f"{database_info['sqlite_version']}"
                    )
                )

                tables = database_info["tables"]

                self.tables_label.configure(
                    text=(
                        f"Database tables ({len(tables)}): "
                        + ", ".join(tables)
                    )
                )

            else:

                self.status_label.configure(
                    text="● Database Connection Failed",
                    text_color=COLORS["danger"]
                )

        except Exception as error:

            self.status_label.configure(
                text="● Database Connection Failed",
                text_color=COLORS["danger"]
            )

            self.version_label.configure(
                text="SQLite version: Unavailable"
            )

            self.tables_label.configure(
                text=f"Database error: {error}"
            )

    def open_location(self, location):

        try:

            path = os.fspath(location)

            # If a file was selected, open its parent folder.
            if os.path.isfile(path):
                path = os.path.dirname(path)

            # Ensure the folder exists.
            os.makedirs(
                path,
                exist_ok=True
            )

            # Open the folder in Windows File Explorer.
            os.startfile(path)

        except OSError as error:

            messagebox.showerror(
                "Unable to Open Folder",
                str(error),
                parent=self
            )
