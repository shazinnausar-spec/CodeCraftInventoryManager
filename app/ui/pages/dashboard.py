
import customtkinter as ctk
from tkinter import messagebox

from app.ui.theme import COLORS, FONT_FAMILY
from app.ui.components.stat_card import StatCard

from app.services.dashboard_service import (
    get_dashboard_statistics,
    get_low_stock_products,
    get_recent_stock_movements
)


class DashboardPage(ctk.CTkScrollableFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        # Configure dashboard columns.
        self.grid_columnconfigure(
            (0, 1, 2, 3),
            weight=1,
            uniform="dashboard"
        )

        # Store card references.
        self.stat_cards = {}

        # Create dashboard sections.
        self.create_welcome_section()
        self.create_statistics()
        self.create_information_sections()

        # Load database information.
        self.refresh_dashboard()

    # --------------------------------------------------
    # WELCOME SECTION
    # --------------------------------------------------

    def create_welcome_section(self):

        welcome_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        welcome_frame.grid(
            row=0,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=25,
            pady=(25, 5)
        )

        welcome_frame.grid_columnconfigure(
            0,
            weight=1
        )

        ctk.CTkLabel(
            welcome_frame,
            text="Inventory Overview",
            font=(FONT_FAMILY, 25, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkButton(
            welcome_frame,
            text="Refresh",
            width=100,
            height=34,
            command=self.refresh_dashboard,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        ).grid(
            row=0,
            column=1,
            sticky="e"
        )

        ctk.CTkLabel(
            self,
            text="Monitor your products and inventory performance.",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["secondary_text"]
        ).grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="w",
            padx=25,
            pady=(0, 25)
        )

    # --------------------------------------------------
    # STATISTICS CARDS
    # --------------------------------------------------

    def create_statistics(self):

        cards = [
            (
                "Total Products",
                "—",
                "Registered products",
                COLORS["primary"]
            ),
            (
                "Stock Quantity",
                "—",
                "Units currently available",
                COLORS["accent"]
            ),
            (
                "Low Stock",
                "—",
                "Products requiring attention",
                COLORS["warning"]
            ),
            (
                "Inventory Value",
                "—",
                "Based on purchase prices",
                COLORS["success"]
            )
        ]

        for index, card_data in enumerate(cards):

            title, value, description, accent = card_data

            card = StatCard(
                self,
                title=title,
                value=value,
                description=description,
                accent_color=accent
            )

            card.grid(
                row=2,
                column=index,
                padx=8,
                pady=5,
                sticky="nsew"
            )

            self.stat_cards[title] = card

        # Adjust card columns when the page resizes.
        self.bind(
            "<Configure>",
            self.adjust_card_layout
        )


    def adjust_card_layout(self, event):

        # Ignore child-widget resize events.
        if event.widget != self:
            return

        width = event.width

        # Determine the number of dashboard columns.
        if width >= 1050:
            columns = 4
        elif width >= 650:
            columns = 2
        else:
            columns = 1

        # Configure active and inactive columns.
        for column in range(4):

            self.grid_columnconfigure(
                column,
                weight=1 if column < columns else 0,
                uniform="dashboard" if column < columns else ""
            )

        # Reposition the statistics cards.
        for index, card in enumerate(self.stat_cards.values()):

            card.grid(
                row=2 + (index // columns),
                column=index % columns,
                columnspan=1,
                padx=8,
                pady=5,
                sticky="nsew"
            )

        # Calculate the row after the statistics cards.
        information_row = (
            2 + (len(self.stat_cards) + columns - 1) // columns
        )

        # Wide and medium layouts: information panels side by side.
        if columns >= 2:

            self.low_stock_panel.grid(
                row=information_row,
                column=0,
                columnspan=columns // 2,
                padx=8,
                pady=25,
                sticky="nsew"
            )

            self.movement_panel.grid(
                row=information_row,
                column=columns // 2,
                columnspan=columns // 2,
                padx=8,
                pady=25,
                sticky="nsew"
            )

        # Narrow layout: stack information panels vertically.
        else:

            self.low_stock_panel.grid(
                row=information_row,
                column=0,
                columnspan=1,
                padx=8,
                pady=(20, 10),
                sticky="nsew"
            )

            self.movement_panel.grid(
                row=information_row + 1,
                column=0,
                columnspan=1,
                padx=8,
                pady=(10, 20),
                sticky="nsew"
            )
    # --------------------------------------------------
    # INFORMATION PANELS
    # --------------------------------------------------

    def create_information_sections(self):

        self.low_stock_panel = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.movement_panel = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        ctk.CTkLabel(
            self.low_stock_panel,
            text="Low Stock Products",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            self.movement_panel,
            text="Recent Stock Movements",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"]
        ).pack(
            anchor="w",
            padx=20,
            pady=(20, 10)
        )

        self.low_stock_content = ctk.CTkFrame(
            self.low_stock_panel,
            fg_color="transparent"
        )

        self.low_stock_content.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.movement_content = ctk.CTkFrame(
            self.movement_panel,
            fg_color="transparent"
        )

        self.movement_content.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

    # --------------------------------------------------
    # REFRESH DASHBOARD
    # --------------------------------------------------

    def refresh_dashboard(self):

        try:

            statistics = get_dashboard_statistics()

            self.stat_cards["Total Products"].update_value(
                f"{statistics['total_products']:,}"
            )

            self.stat_cards["Stock Quantity"].update_value(
                f"{statistics['total_stock']:,}"
            )

            self.stat_cards["Low Stock"].update_value(
                f"{statistics['low_stock_products']:,}"
            )

            inventory_value = (
                statistics["inventory_value"] / 100
            )

            self.stat_cards["Inventory Value"].update_value(
                f"LKR {inventory_value:,.2f}"
            )

            self.load_low_stock_products()
            self.load_recent_movements()

        except Exception as error:

            messagebox.showerror(
                "Dashboard Error",
                f"Could not refresh dashboard:\n{error}"
            )

    # --------------------------------------------------
    # LOW STOCK PRODUCTS
    # --------------------------------------------------

    def load_low_stock_products(self):

        for widget in self.low_stock_content.winfo_children():
            widget.destroy()

        products = get_low_stock_products(limit=5)

        if not products:

            ctk.CTkLabel(
                self.low_stock_content,
                text="No low-stock products. Everything looks good!",
                font=(FONT_FAMILY, 12),
                text_color=COLORS["success"],
                wraplength=350
            ).pack(
                anchor="w",
                padx=5,
                pady=15
            )

            return

        for product in products:

            product_frame = ctk.CTkFrame(
                self.low_stock_content,
                fg_color=COLORS["background"],
                corner_radius=8
            )

            product_frame.pack(
                fill="x",
                pady=4
            )

            product_frame.grid_columnconfigure(
                0,
                weight=1
            )

            ctk.CTkLabel(
                product_frame,
                text=product["name"],
                font=(FONT_FAMILY, 12, "bold"),
                text_color=COLORS["text"],
                anchor="w",
                wraplength=250
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=10,
                pady=(8, 2)
            )

            ctk.CTkLabel(
                product_frame,
                text=product["sku"],
                font=(FONT_FAMILY, 10),
                text_color=COLORS["secondary_text"]
            ).grid(
                row=1,
                column=0,
                sticky="w",
                padx=10,
                pady=(0, 8)
            )

            ctk.CTkLabel(
                product_frame,
                text=(
                    f"{product['quantity']} / "
                    f"{product['minimum_stock']} units"
                ),
                font=(FONT_FAMILY, 11, "bold"),
                text_color=COLORS["warning"]
            ).grid(
                row=0,
                column=1,
                rowspan=2,
                padx=10,
                pady=8
            )

    # --------------------------------------------------
    # RECENT STOCK MOVEMENTS
    # --------------------------------------------------

    def load_recent_movements(self):

        for widget in self.movement_content.winfo_children():
            widget.destroy()

        movements = get_recent_stock_movements(limit=5)

        if not movements:

            ctk.CTkLabel(
                self.movement_content,
                text="No stock movements recorded yet.",
                font=(FONT_FAMILY, 12),
                text_color=COLORS["muted_text"]
            ).pack(
                anchor="w",
                padx=5,
                pady=15
            )

            return

        for movement in movements:

            movement_frame = ctk.CTkFrame(
                self.movement_content,
                fg_color=COLORS["background"],
                corner_radius=8
            )

            movement_frame.pack(
                fill="x",
                pady=4
            )

            movement_frame.grid_columnconfigure(
                0,
                weight=1
            )

            movement_type = movement["movement_type"]

            if movement_type == "STOCK_IN":

                type_text = "Stock In"
                type_color = COLORS["success"]
                quantity_text = f"+{movement['quantity']}"

            elif movement_type == "STOCK_OUT":

                type_text = "Stock Out"
                type_color = COLORS["danger"]
                quantity_text = f"-{movement['quantity']}"

            else:

                type_text = "Opening"
                type_color = COLORS["primary"]
                quantity_text = f"+{movement['quantity']}"

            ctk.CTkLabel(
                movement_frame,
                text=movement["product_name"],
                font=(FONT_FAMILY, 12, "bold"),
                text_color=COLORS["text"],
                anchor="w",
                wraplength=250
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=10,
                pady=(8, 2)
            )

            ctk.CTkLabel(
                movement_frame,
                text=type_text,
                font=(FONT_FAMILY, 10),
                text_color=type_color
            ).grid(
                row=1,
                column=0,
                sticky="w",
                padx=10,
                pady=(0, 8)
            )

            ctk.CTkLabel(
                movement_frame,
                text=quantity_text,
                font=(FONT_FAMILY, 12, "bold"),
                text_color=type_color
            ).grid(
                row=0,
                column=1,
                rowspan=2,
                padx=10,
                pady=8
            )
