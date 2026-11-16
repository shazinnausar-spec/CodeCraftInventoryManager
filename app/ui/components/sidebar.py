
# Import CustomTkinter.
import customtkinter as ctk

# Import application information.
from app.config import APP_NAME, APP_VERSION, APP_AUTHOR

# Import theme settings.
from app.ui.theme import COLORS, FONT_FAMILY, SIDEBAR_WIDTH


class Sidebar(ctk.CTkFrame):

    def __init__(self, parent, on_navigate):

        super().__init__(
            parent,
            width=SIDEBAR_WIDTH,
            corner_radius=0,
            fg_color=COLORS["sidebar"]
        )

        # Save the navigation callback.
        self.on_navigate = on_navigate

        # Store navigation buttons.
        self.navigation_buttons = {}

        # Store the current active page.
        self.active_page = "dashboard"

        # Prevent automatic resizing.
        self.grid_propagate(False)

        # Build sidebar sections.
        self.create_branding()
        self.create_navigation()
        self.create_footer()

    def create_branding(self):

        # Brand heading.
        brand = ctk.CTkLabel(
            self,
            text="CODECRAFT",
            font=(FONT_FAMILY, 23, "bold"),
            text_color="#FFFFFF"
        )

        brand.pack(
            anchor="w",
            padx=25,
            pady=(32, 4)
        )

        # Small accent line below the brand.
        accent = ctk.CTkFrame(
            self,
            width=42,
            height=3,
            corner_radius=2,
            fg_color=COLORS["accent"]
        )

        accent.pack(
            anchor="w",
            padx=27,
            pady=(5, 10)
        )

        # Application subtitle.
        subtitle = ctk.CTkLabel(
            self,
            text="INVENTORY MANAGER",
            font=(FONT_FAMILY, 10, "bold"),
            text_color=COLORS["muted_text"]
        )

        subtitle.pack(
            anchor="w",
            padx=27,
            pady=(0, 32)
        )

    def create_navigation(self):

        # Navigation section heading.
        section = ctk.CTkLabel(
            self,
            text="WORKSPACE",
            font=(FONT_FAMILY, 10, "bold"),
            text_color=COLORS["muted_text"]
        )

        section.pack(
            anchor="w",
            padx=25,
            pady=(0, 12)
        )

        # Navigation menu items.
        navigation_items = [
            ("dashboard", "Dashboard"),
            ("products", "Products"),
            ("categories", "Categories"),
            ("stock_management", "Stock Management"),
            ("stock_history", "Stock History"),
            ("reports", "Reports"),
            ("backup", "Backup & Restore"),
            ("settings", "Settings"),
            ("about", "About"),
        ]

        # Create a button for every page.
        for page_id, page_name in navigation_items:

            button = ctk.CTkButton(
                self,
                text=page_name,
                height=43,
                corner_radius=8,
                anchor="w",
                font=(FONT_FAMILY, 13),
                text_color="#CBD5E1",
                fg_color="transparent",
                hover_color=COLORS["sidebar_hover"],
                border_spacing=12,
                command=lambda p=page_id: self.navigate(p)
            )

            button.pack(
                padx=14,
                pady=3,
                fill="x"
            )

            # Store the button for later styling.
            self.navigation_buttons[page_id] = button

        # Highlight the initial page.
        self.update_active_button("dashboard")

    def navigate(self, page_id):

        # Ignore unknown page IDs.
        if page_id not in self.navigation_buttons:
            return

        # Update the active page.
        self.update_active_button(page_id)

        # Notify the main window.
        self.on_navigate(page_id)

    def update_active_button(self, page_id):

        # Ignore unknown page IDs.
        if page_id not in self.navigation_buttons:
            return

        self.active_page = page_id

        # Update every navigation button.
        for current_id, button in self.navigation_buttons.items():

            if current_id == page_id:

                button.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color="#FFFFFF",
                    font=(FONT_FAMILY, 13, "bold")
                )

            else:

                button.configure(
                    fg_color="transparent",
                    text_color="#CBD5E1",
                    font=(FONT_FAMILY, 13)
                )

    def create_footer(self):

        # Footer container.
        footer = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        footer.pack(
            side="bottom",
            fill="x",
            padx=20,
            pady=22
        )

        # Developer name.
        brand = ctk.CTkLabel(
            footer,
            text=APP_AUTHOR.upper(),
            font=(FONT_FAMILY, 10, "bold"),
            text_color=COLORS["muted_text"]
        )

        brand.pack(anchor="w")

        # Application version.
        version = ctk.CTkLabel(
            footer,
            text=f"Version {APP_VERSION}",
            font=(FONT_FAMILY, 10),
            text_color="#64748B"
        )

        version.pack(
            anchor="w",
            pady=(3, 0)
        )
