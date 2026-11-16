
# Import CustomTkinter.
import customtkinter as ctk

# Import theme settings.
from app.ui.theme import COLORS, FONT_FAMILY


class Header(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            height=75,
            corner_radius=0,
            fg_color=COLORS["card"],
            border_width=0
        )

        # Prevent automatic height changes.
        self.grid_propagate(False)

        # Configure flexible header layout.
        self.grid_columnconfigure(1, weight=1)

        # Accent indicator beside the page title.
        self.title_accent = ctk.CTkFrame(
            self,
            width=4,
            height=27,
            corner_radius=2,
            fg_color=COLORS["primary"]
        )

        self.title_accent.grid(
            row=0,
            column=0,
            padx=(30, 0),
            pady=24
        )

        # Page title.
        self.title_label = ctk.CTkLabel(
            self,
            text="Dashboard",
            font=(FONT_FAMILY, 21, "bold"),
            text_color=COLORS["text"],
            anchor="w"
        )

        self.title_label.grid(
            row=0,
            column=1,
            padx=(13, 10),
            pady=20,
            sticky="w"
        )

        # Brand information.
        self.brand_label = ctk.CTkLabel(
            self,
            text="CODECRAFT STUDIO",
            font=(FONT_FAMILY, 11, "bold"),
            text_color=COLORS["secondary_text"]
        )

        self.brand_label.grid(
            row=0,
            column=2,
            padx=(15, 30),
            pady=20,
            sticky="e"
        )

        # Subtle bottom border.
        self.bottom_border = ctk.CTkFrame(
            self,
            height=1,
            corner_radius=0,
            fg_color=COLORS["border"]
        )

        self.bottom_border.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky="ew"
        )

    def set_title(self, title):
        """Update the displayed page title."""

        self.title_label.configure(
            text=title
        )
