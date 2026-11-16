import customtkinter as ctk
from tkinter import messagebox

from app.services.category_service import (
    create_category,
    get_all_categories
)

from app.ui.theme import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_SMALL,
    FONT_SIZE_NORMAL,
    FONT_SIZE_MEDIUM,
    FONT_SIZE_LARGE
)


class CategoriesPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.create_header()
        self.create_search_section()
        self.create_category_table()

        self.load_categories()

    def create_header(self):
        """Create the page heading and Add Category button."""

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=30,
            pady=(25, 15)
        )

        header.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header,
            text="Category Management",
            font=(FONT_FAMILY, 26, "bold"),
            text_color=COLORS["text"]
        )
        title.grid(row=0, column=0, sticky="w")

        description = ctk.CTkLabel(
            header,
            text="Organize your products into categories.",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["secondary_text"]
        )
        description.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(5, 0)
        )

        add_button = ctk.CTkButton(
            header,
            text="+ Add Category",
            width=145,
            height=38,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            command=self.open_add_category_dialog
        )
        add_button.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(15, 0)
        )

    def create_search_section(self):
        """Create the category search and refresh controls."""

        search_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        search_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18)
        )

        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search categories...",
            height=38,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            border_color=COLORS["border"]
        )
        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(15, 10),
            pady=15
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.on_search
        )

        refresh_button = ctk.CTkButton(
            search_frame,
            text="Refresh",
            width=90,
            height=38,
            fg_color=COLORS["sidebar"],
            hover_color=COLORS["sidebar_hover"],
            command=self.load_categories
        )
        refresh_button.grid(
            row=0,
            column=1,
            padx=(10, 15),
            pady=15
        )

    def create_category_table(self):
        """Create the category listing area."""

        self.table_container = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        self.table_container.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=30,
            pady=(0, 25)
        )

        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)

        table_title = ctk.CTkLabel(
            self.table_container,
            text="Category List",
            font=(FONT_FAMILY, FONT_SIZE_LARGE, "bold"),
            text_color=COLORS["text"]
        )
        table_title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=18
        )

        self.table_scroll = ctk.CTkScrollableFrame(
            self.table_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.table_scroll.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 12)
        )

        self.table_scroll.grid_columnconfigure(0, weight=1)

    def load_categories(self):
        """Retrieve categories from the database."""

        try:
            categories = get_all_categories()
            self.display_categories(categories)

        except Exception as error:
            messagebox.showerror(
                "Category Error",
                f"Unable to load categories.\n\n{error}"
            )

    def display_categories(self, categories):
        """Display category records in the table."""

        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        # Filter categories using the search text.
        search_text = self.search_entry.get().strip().lower()

        filtered_categories = [
            category for category in categories
            if search_text in category["name"].lower()
        ]

        # Table headings.
        header = ctk.CTkFrame(
            self.table_scroll,
            fg_color=COLORS["background"],
            corner_radius=6
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=3)

        headings = ["CATEGORY", "DESCRIPTION"]

        for index, heading in enumerate(headings):
            label = ctk.CTkLabel(
                header,
                text=heading,
                font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
                text_color=COLORS["secondary_text"],
                anchor="w"
            )
            label.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=15,
                pady=12
            )

        if not filtered_categories:
            empty_label = ctk.CTkLabel(
                self.table_scroll,
                text=(
                    "No categories found."
                    if search_text
                    else "No categories created yet."
                ),
                font=(FONT_FAMILY, FONT_SIZE_MEDIUM),
                text_color=COLORS["secondary_text"]
            )
            empty_label.grid(
                row=1,
                column=0,
                pady=55
            )
            return

        # Display each category.
        for row_index, category in enumerate(
            filtered_categories,
            start=1
        ):
            row = ctk.CTkFrame(
                self.table_scroll,
                fg_color=COLORS["card"],
                corner_radius=5
            )
            row.grid(
                row=row_index,
                column=0,
                sticky="ew",
                pady=3
            )

            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=3)

            name_label = ctk.CTkLabel(
                row,
                text=category["name"],
                font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                text_color=COLORS["text"],
                anchor="w"
            )
            name_label.grid(
                row=0,
                column=0,
                sticky="ew",
                padx=15,
                pady=14
            )

            description = category["description"] or "—"

            description_label = ctk.CTkLabel(
                row,
                text=description,
                font=(FONT_FAMILY, FONT_SIZE_NORMAL),
                text_color=COLORS["secondary_text"],
                anchor="w"
            )
            description_label.grid(
                row=0,
                column=1,
                sticky="ew",
                padx=15,
                pady=14
            )

    def on_search(self, event=None):
        """Refresh the displayed list while searching."""

        self.load_categories()

    def open_add_category_dialog(self):
        """Open the Add Category form."""

        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Category")
        dialog.geometry("450x390")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["background"])

        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            dialog,
            text="Add New Category",
            font=(FONT_FAMILY, 22, "bold"),
            text_color=COLORS["text"]
        )
        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=25,
            pady=(25, 5)
        )

        subtitle = ctk.CTkLabel(
            dialog,
            text="Enter the category details below.",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["secondary_text"]
        )
        subtitle.grid(
            row=1,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 20)
        )

        name_label = ctk.CTkLabel(
            dialog,
            text="Category Name *",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            text_color=COLORS["text"]
        )
        name_label.grid(
            row=2,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 6)
        )

        name_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. Electronics",
            height=40,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL)
        )
        name_entry.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 15)
        )

        description_label = ctk.CTkLabel(
            dialog,
            text="Description",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            text_color=COLORS["text"]
        )
        description_label.grid(
            row=4,
            column=0,
            sticky="w",
            padx=25,
            pady=(0, 6)
        )

        description_entry = ctk.CTkTextbox(
            dialog,
            height=90,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            border_width=1,
            border_color=COLORS["border"]
        )
        description_entry.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=25,
            pady=(0, 20)
        )

        def save_category():
            """Validate and save the category."""

            name = name_entry.get().strip()

            description = description_entry.get(
                "1.0",
                "end"
            ).strip()

            try:
                create_category(
                    name=name,
                    description=description
                )

                messagebox.showinfo(
                    "Success",
                    "Category created successfully.",
                    parent=dialog
                )

                dialog.destroy()
                self.load_categories()

            except ValueError as error:
                messagebox.showwarning(
                    "Invalid Category",
                    str(error),
                    parent=dialog
                )

            except Exception as error:
                messagebox.showerror(
                    "Error",
                    f"Unable to save category.\n\n{error}",
                    parent=dialog
                )

        button_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )
        button_frame.grid(
            row=6,
            column=0,
            sticky="e",
            padx=25,
            pady=(0, 20)
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=90,
            height=36,
            fg_color=COLORS["sidebar"],
            hover_color=COLORS["sidebar_hover"],
            command=dialog.destroy
        )
        cancel_button.pack(
            side="left",
            padx=(0, 10)
        )

        save_button = ctk.CTkButton(
            button_frame,
            text="Save Category",
            width=125,
            height=36,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=save_category
        )
        save_button.pack(side="left")

        name_entry.focus()