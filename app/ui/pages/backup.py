# Import operating system utilities.
import os

# Import CustomTkinter.
import customtkinter as ctk

# Import tkinter dialogs.
from tkinter import filedialog, messagebox

# Import backup configuration.
from app.config import BACKUP_DIR

# Import backup service functions.
from app.services.backup_service import (
    create_backup,
    validate_backup,
    restore_backup
)

# Import theme settings.
from app.ui.theme import (
    COLORS,
    FONT_FAMILY
)


class BackupPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        # Store the selected backup file.
        self.selected_backup = None

        # Allow the page to expand.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Build the page.
        self.create_heading()
        self.create_actions()
        self.create_backup_list()

        # Load existing backups.
        self.refresh_backups()


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
            text="Backup & Restore",
            font=(FONT_FAMILY, 25, "bold"),
            text_color=COLORS["text"]
        )

        title.pack(anchor="w")

        description = ctk.CTkLabel(
            heading,
            text=(
                "Protect your inventory database by creating "
                "backups and restoring previous versions."
            ),
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"]
        )

        description.pack(
            anchor="w",
            pady=(5, 0)
        )


    def create_actions(self):

        actions = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        actions.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18)
        )

        actions.grid_columnconfigure(
            0,
            weight=1
        )

        title = ctk.CTkLabel(
            actions,
            text="Database Backup",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"]
        )

        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(18, 5)
        )

        description = ctk.CTkLabel(
            actions,
            text=(
                "Create a safe copy of your current inventory database."
            ),
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"]
        )

        description.grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(0, 15)
        )

        button_frame = ctk.CTkFrame(
            actions,
            fg_color="transparent"
        )

        button_frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 18)
        )

        create_button = ctk.CTkButton(
            button_frame,
            text="+ Create Backup",
            height=38,
            width=150,
            font=(FONT_FAMILY, 12, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=self.create_new_backup
        )

        create_button.pack(
            side="left",
            padx=(0, 10)
        )

        refresh_button = ctk.CTkButton(
            button_frame,
            text="Refresh",
            height=38,
            width=100,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text"],
            fg_color=COLORS["border"],
            hover_color="#CBD5E1",
            command=self.refresh_backups
        )

        refresh_button.pack(
            side="left",
            padx=(0, 10)
        )

        folder_button = ctk.CTkButton(
            button_frame,
            text="Open Backup Folder",
            height=38,
            width=150,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text"],
            fg_color=COLORS["border"],
            hover_color="#CBD5E1",
            command=self.open_backup_folder
        )

        folder_button.pack(side="left")
        
        browse_button = ctk.CTkButton(
            button_frame,
            text="Browse Backup",
            height=38,
            width=130,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["text"],
            fg_color=COLORS["border"],
            hover_color="#CBD5E1",
            command=self.browse_backup
        )

        browse_button.pack(side="left")


    def create_backup_list(self):

        container = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )

        container.grid_columnconfigure(
            0,
            weight=1
        )

        container.grid_rowconfigure(
            1,
            weight=1
        )

        heading = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        heading.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=18
        )

        title = ctk.CTkLabel(
            heading,
            text="Available Backups",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"]
        )

        title.pack(
            side="left"
        )

        self.backup_count_label = ctk.CTkLabel(
            heading,
            text="0 backups",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["secondary_text"]
        )

        self.backup_count_label.pack(
            side="right"
        )

        # Scrollable backup list.
        self.backup_list = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent"
        )

        self.backup_list.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 10)
        )

        self.backup_list.grid_columnconfigure(
            0,
            weight=1
        )

        # Selected backup information.
        self.selection_label = ctk.CTkLabel(
            container,
            text="Select a backup to validate or restore it.",
            font=(FONT_FAMILY, 11),
            text_color=COLORS["secondary_text"],
            anchor="w"
        )

        self.selection_label.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(5, 12)
        )

        # Backup actions.
        buttons = ctk.CTkFrame(
            container,
            fg_color="transparent"
        )

        buttons.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 18)
        )

        self.validate_button = ctk.CTkButton(
            buttons,
            text="Validate Backup",
            height=38,
            width=140,
            fg_color=COLORS["accent"],
            hover_color="#0891B2",
            text_color="#FFFFFF",
            command=self.validate_selected_backup,
            state="disabled"
        )

        self.validate_button.pack(
            side="left",
            padx=(0, 10)
        )

        self.restore_button = ctk.CTkButton(
            buttons,
            text="Restore Selected Backup",
            height=38,
            width=190,
            fg_color=COLORS["danger"],
            hover_color="#B91C1C",
            text_color="#FFFFFF",
            command=self.restore_selected_backup,
            state="disabled"
        )

        self.restore_button.pack(
            side="left"
        )


    def refresh_backups(self):

        # Remove old backup entries.
        for widget in self.backup_list.winfo_children():
            widget.destroy()

        self.selected_backup = None

        self.validate_button.configure(
            state="disabled"
        )

        self.restore_button.configure(
            state="disabled"
        )

        self.selection_label.configure(
            text="Select a backup to validate or restore it."
        )

        # Find database backup files.
        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        backups = sorted(
            BACKUP_DIR.glob("*.db"),
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        self.backup_count_label.configure(
            text=f"{len(backups)} backups"
        )

        if not backups:

            empty_label = ctk.CTkLabel(
                self.backup_list,
                text="No backups available yet.",
                font=(FONT_FAMILY, 13),
                text_color=COLORS["secondary_text"]
            )

            empty_label.pack(
                pady=40
            )

            return

        # Display every backup.
        for backup_path in backups:

            self.create_backup_item(
                backup_path
            )


    def create_backup_item(self, backup_path):

        item = ctk.CTkFrame(
            self.backup_list,
            fg_color="#F8FAFC",
            corner_radius=8,
            border_width=1,
            border_color=COLORS["border"]
        )

        item.pack(
            fill="x",
            padx=5,
            pady=5
        )

        item.grid_columnconfigure(
            0,
            weight=1
        )

        # Backup filename.
        name = ctk.CTkLabel(
            item,
            text=backup_path.name,
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"],
            anchor="w"
        )

        name.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=15,
            pady=(12, 3)
        )

        # Backup file information.
        file_size = backup_path.stat().st_size / 1024

        modified_time = backup_path.stat().st_mtime

        from datetime import datetime

        modified_date = datetime.fromtimestamp(
            modified_time
        ).strftime("%Y-%m-%d %I:%M %p")

        details = ctk.CTkLabel(
            item,
            text=(
                f"Created: {modified_date}    "
                f"Size: {file_size:.2f} KB"
            ),
            font=(FONT_FAMILY, 10),
            text_color=COLORS["secondary_text"],
            anchor="w"
        )

        details.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 12)
        )

        select_button = ctk.CTkButton(
            item,
            text="Select",
            width=85,
            height=32,
            font=(FONT_FAMILY, 11),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=lambda path=backup_path: self.select_backup(path)
        )

        select_button.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=15
        )


    def select_backup(self, backup_path):

        self.selected_backup = backup_path

        self.selection_label.configure(
            text=f"Selected: {backup_path.name}"
        )

        self.validate_button.configure(
            state="normal"
        )

        self.restore_button.configure(
            state="normal"
        )


    def create_new_backup(self):

        try:

            backup_path = create_backup()

            self.refresh_backups()

            self.select_backup(backup_path)

            messagebox.showinfo(
                "Backup Created",
                (
                    "Your database backup was created successfully.\n\n"
                    f"File: {backup_path.name}"
                ),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Backup Failed",
                str(error),
                parent=self
            )


    def validate_selected_backup(self):

        if not self.selected_backup:
            return

        try:

            validate_backup(
                self.selected_backup
            )

            messagebox.showinfo(
                "Backup Valid",
                (
                    "The selected backup passed validation.\n\n"
                    "The database file is readable and contains "
                    "the required tables."
                ),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Invalid Backup",
                str(error),
                parent=self
            )


    def restore_selected_backup(self):

        if not self.selected_backup:
            return

        # Confirm before replacing the active database.
        confirmed = messagebox.askyesno(
            "Confirm Database Restore",
            (
                "WARNING: Restoring this backup will replace "
                "your current inventory database.\n\n"
                "A safety backup of the current database will "
                "be created automatically.\n\n"
                "Do you want to continue?"
            ),
            icon="warning",
            parent=self
        )

        if not confirmed:
            return

        try:

            safety_backup = restore_backup(
                self.selected_backup
            )

            if safety_backup:

                safety_message = (
                    f"\n\nSafety backup created:\n"
                    f"{safety_backup.name}"
                )

            else:

                safety_message = ""

            messagebox.showinfo(
                "Restore Successful",
                (
                    "The database was restored successfully."
                    f"{safety_message}\n\n"
                    "The dashboard will now refresh."
                ),
                parent=self
            )

            # Reload the dashboard to display restored data.
            self.winfo_toplevel().show_page(
                "dashboard"
            )

        except Exception as error:

            messagebox.showerror(
                "Restore Failed",
                str(error),
                parent=self
            )


    def open_backup_folder(self):

        BACKUP_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        try:

            os.startfile(
                str(BACKUP_DIR)
            )

        except OSError as error:

            messagebox.showerror(
                "Unable to Open Folder",
                str(error),
                parent=self
            )

    def browse_backup(self):

        backup_path = filedialog.askopenfilename(
            title="Select Database Backup",
            filetypes=[
                ("SQLite Database", "*.db"),
                ("All Files", "*.*")
            ]
        )

        if not backup_path:
            return

        self.select_backup(
            __import__("pathlib").Path(backup_path)
        )   