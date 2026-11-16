
# Import CustomTkinter.
import customtkinter as ctk

# Import theme settings.
from app.ui.theme import COLORS, FONT_FAMILY, FONT_SIZE_NORMAL, FONT_SIZE_SMALL


class ActionButton(ctk.CTkButton):
    """Reusable button component with consistent application styling."""

    # Available button styles.
    VARIANTS = {
        "primary": {
            "fg_color": COLORS["primary"],
            "hover_color": COLORS["primary_hover"],
            "text_color": "#FFFFFF",
        },

        "secondary": {
            "fg_color": COLORS["sidebar"],
            "hover_color": COLORS["sidebar_hover"],
            "text_color": "#FFFFFF",
        },

        "danger": {
            "fg_color": COLORS["danger"],
            "hover_color": "#B91C1C",
            "text_color": "#FFFFFF",
        },

        "success": {
            "fg_color": COLORS["success"],
            "hover_color": "#15803D",
            "text_color": "#FFFFFF",
        },
    }

    # Available button sizes.
    SIZES = {
        "small": {
            "height": 28,
            "font_size": FONT_SIZE_SMALL,
            "corner_radius": 6,
        },

        "normal": {
            "height": 38,
            "font_size": FONT_SIZE_NORMAL,
            "corner_radius": 8,
        },

        "large": {
            "height": 44,
            "font_size": 14,
            "corner_radius": 9,
        },
    }

    def __init__(
        self,
        parent,
        text,
        variant="primary",
        size="normal",
        command=None,
        width=None,
        **kwargs
    ):
        # Validate the requested button style.
        if variant not in self.VARIANTS:
            raise ValueError(
                f"Unknown button variant: {variant}"
            )

        # Validate the requested button size.
        if size not in self.SIZES:
            raise ValueError(
                f"Unknown button size: {size}"
            )

        # Get the selected button style.
        style = self.VARIANTS[variant].copy()

        # Get the selected button dimensions.
        dimensions = self.SIZES[size].copy()

        # Build the button configuration.
        button_options = {
            "text": text,
            "command": command,
            "width": width if width is not None else 120,
            "height": dimensions["height"],
            "corner_radius": dimensions["corner_radius"],
            "font": (
                FONT_FAMILY,
                dimensions["font_size"],
                "bold"
            ),
            "fg_color": style["fg_color"],
            "hover_color": style["hover_color"],
            "text_color": style["text_color"],
        }

        # Allow custom options to override default styling.
        button_options.update(kwargs)

        # Create the button.
        super().__init__(
            parent,
            **button_options
        )
