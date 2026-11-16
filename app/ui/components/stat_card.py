
# Import CustomTkinter.
import customtkinter as ctk

# Import theme settings.
from app.ui.theme import COLORS, FONT_FAMILY


class StatCard(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        title,
        value="—",
        description="",
        accent_color=None
    ):

        super().__init__(
            parent,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"],
            height=155
        )

        # Prevent child widgets from changing card height.
        self.grid_propagate(False)

        # Store card title.
        self.title = title

        # Store accent colour.
        self.accent_color = accent_color or COLORS["primary"]

        # Configure card layout.
        self.grid_columnconfigure(1, weight=1)

        # Accent indicator.
        self.accent = ctk.CTkFrame(
            self,
            width=4,
            height=38,
            corner_radius=3,
            fg_color=self.accent_color
        )

        self.accent.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="w",
            padx=(18, 0),
            pady=(20, 0)
        )

        # Card heading.
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"],
            anchor="w"
        )

        self.title_label.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(12, 18),
            pady=(20, 4)
        )

        # Main card value.
        self.value_label = ctk.CTkLabel(
            self,
            text=str(value),
            font=(FONT_FAMILY, 25, "bold"),
            text_color=COLORS["text"],
            anchor="w"
        )

        self.value_label.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(12, 18),
            pady=(0, 5)
        )

        # Supporting description.
        self.description_label = ctk.CTkLabel(
            self,
            text=description,
            font=(FONT_FAMILY, 11),
            text_color=COLORS["muted_text"],
            anchor="w",
            wraplength=220
        )

        self.description_label.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(5, 18)
        )

    def update_value(self, value):
        """Update the displayed statistics value."""

        self.value_label.configure(
            text=str(value)
        )

    def update_description(self, description):
        """Update the supporting description."""

        self.description_label.configure(
            text=description
        )
