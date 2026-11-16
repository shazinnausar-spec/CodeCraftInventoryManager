
# Import CustomTkinter.
import customtkinter as ctk

# Import application information.
from app.config import (
    APP_NAME,
    APP_VERSION,
    APP_AUTHOR
)

# Import theme settings.
from app.ui.theme import (
    COLORS,
    FONT_FAMILY
)


class AboutPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        # Allow the content to expand.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build the About page.
        self.create_content()

    def create_content(self):

        # Main scrollable container.
        container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        container.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=30,
            pady=25
        )

        container.grid_columnconfigure(
            0,
            weight=1
        )

        # Application branding.
        self.create_branding(container)

        # Application description.
        self.create_description(container)

        # Features.
        self.create_features(container)

        # Technologies.
        self.create_technologies(container)

        # Developer information.
        self.create_developer_section(container)

        # Footer.
        self.create_footer(container)

    def create_branding(self, parent):

        branding = ctk.CTkFrame(
            parent,
            fg_color=COLORS["sidebar"],
            corner_radius=15
        )

        branding.pack(
            fill="x",
            pady=(0, 18)
        )

        logo = ctk.CTkLabel(
            branding,
            text="CC",
            width=75,
            height=75,
            corner_radius=18,
            fg_color=COLORS["primary"],
            text_color="#FFFFFF",
            font=(FONT_FAMILY, 30, "bold")
        )

        logo.pack(
            pady=(35, 15)
        )

        brand = ctk.CTkLabel(
            branding,
            text="CODECRAFT",
            font=(FONT_FAMILY, 26, "bold"),
            text_color="#FFFFFF"
        )

        brand.pack()

        title = ctk.CTkLabel(
            branding,
            text="INVENTORY MANAGER",
            font=(FONT_FAMILY, 13, "bold"),
            text_color="#CBD5E1"
        )

        title.pack(
            pady=(5, 12)
        )

        version = ctk.CTkLabel(
            branding,
            text=f"Version {APP_VERSION}",
            font=(FONT_FAMILY, 12),
            text_color="#94A3B8"
        )

        version.pack(
            pady=(0, 35)
        )

    def create_card(self, parent, title, description):

        card = ctk.CTkFrame(
            parent,
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
            pady=(18, 5)
        )

        subtitle = ctk.CTkLabel(
            card,
            text=description,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"],
            justify="left",
            wraplength=850
        )

        subtitle.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

        return card

    def create_description(self, parent):

        card = self.create_card(
            parent,
            "About the Application",
            (
                "CodeCraft Inventory Manager is a desktop inventory "
                "management application designed to help businesses "
                "manage products, stock levels, categories and "
                "inventory reports through a simple interface."
            )
        )

        details = ctk.CTkLabel(
            card,
            text=(
                "The application stores its data locally using "
                "SQLite and provides backup and restore functionality "
                "to help protect inventory information."
            ),
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"],
            justify="left",
            wraplength=850
        )

        details.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

    def create_features(self, parent):

        card = self.create_card(
            parent,
            "Main Features",
            "The application includes the following functionality."
        )

        features = [
            "Product management and category organization",
            "Stock-in and stock-out operations",
            "Stock movement history",
            "Live dashboard statistics",
            "Low-stock monitoring",
            "Inventory and stock reports",
            "CSV report exports",
            "Database backup and restore",
            "Local SQLite data storage"
        ]

        for feature in features:

            row = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )

            row.pack(
                fill="x",
                padx=20,
                pady=4
            )

            check = ctk.CTkLabel(
                row,
                text="✓",
                font=(FONT_FAMILY, 13, "bold"),
                text_color=COLORS["success"]
            )

            check.pack(
                side="left",
                padx=(0, 10)
            )

            label = ctk.CTkLabel(
                row,
                text=feature,
                font=(FONT_FAMILY, 12),
                text_color=COLORS["text"]
            )

            label.pack(
                side="left"
            )

        ctk.CTkFrame(
            card,
            height=15,
            fg_color="transparent"
        ).pack()

    def create_technologies(self, parent):

        card = self.create_card(
            parent,
            "Technology Stack",
            "Technologies and tools used to build this application."
        )

        technologies = [
            ("Language", "Python"),
            ("Desktop Interface", "CustomTkinter"),
            ("Database", "SQLite"),
            ("Image Processing", "Pillow"),
            ("Testing", "Pytest"),
            ("Development Environment", "Visual Studio Code")
        ]

        for name, value in technologies:

            row = ctk.CTkFrame(
                card,
                fg_color="#F8FAFC",
                corner_radius=7
            )

            row.pack(
                fill="x",
                padx=20,
                pady=4
            )

            label = ctk.CTkLabel(
                row,
                text=name,
                font=(FONT_FAMILY, 11),
                text_color=COLORS["secondary_text"]
            )

            label.pack(
                side="left",
                padx=12,
                pady=10
            )

            value_label = ctk.CTkLabel(
                row,
                text=value,
                font=(FONT_FAMILY, 11, "bold"),
                text_color=COLORS["text"]
            )

            value_label.pack(
                side="right",
                padx=12
            )

        ctk.CTkFrame(
            card,
            height=12,
            fg_color="transparent"
        ).pack()

    def create_developer_section(self, parent):

        card = self.create_card(
            parent,
            "Developer",
            "Application development and project information."
        )

        developer = ctk.CTkLabel(
            card,
            text=APP_AUTHOR,
            font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["primary"]
        )

        developer.pack(
            anchor="w",
            padx=20,
            pady=(0, 5)
        )

        application = ctk.CTkLabel(
            card,
            text=APP_NAME,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"]
        )

        application.pack(
            anchor="w",
            padx=20,
            pady=(0, 18)
        )

    def create_footer(self, parent):

        footer = ctk.CTkFrame(
            parent,
            fg_color="transparent"
        )

        footer.pack(
            fill="x",
            pady=(5, 20)
        )

        label = ctk.CTkLabel(
            footer,
            text="CODECRAFT STUDIO",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["secondary_text"]
        )

        label.pack()

        copyright_label = ctk.CTkLabel(
            footer,
            text=f"{APP_NAME} | Version {APP_VERSION}",
            font=(FONT_FAMILY, 10),
            text_color=COLORS["muted_text"]
        )

        copyright_label.pack(
            pady=(5, 0)
        )
