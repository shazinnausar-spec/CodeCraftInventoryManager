
import customtkinter as ctk
from tkinter import messagebox

from app.services.stock_service import get_stock_movements
from app.services.product_service import get_all_products
from app.ui.theme import COLORS


class StockHistoryPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["background"]
        )

        self.movements = []
        self.products = []
        self.product_filter_options = {}

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.create_page_heading()
        self.create_filter_section()
        self.create_history_table()

        self.load_filter_options()
        self.load_history()

    # --------------------------------------------------
    # PAGE HEADING
    # --------------------------------------------------

    def create_page_heading(self):

        heading = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        heading.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=25,
            pady=(20, 10)
        )

        ctk.CTkLabel(
            heading,
            text="Stock History",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            heading,
            text="Review and search your inventory stock movements.",
            font=("Segoe UI", 13),
            text_color=COLORS["secondary_text"]
        ).pack(anchor="w", pady=(4, 0))

    # --------------------------------------------------
    # FILTER SECTION
    # --------------------------------------------------

    def create_filter_section(self):

        self.filter_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.filter_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=10
        )

        self.filter_frame.grid_columnconfigure(
            0,
            weight=2
        )

        self.filter_frame.grid_columnconfigure(
            1,
            weight=1
        )

        self.filter_frame.grid_columnconfigure(
            2,
            weight=1
        )

        self.filter_frame.grid_columnconfigure(
            3,
            weight=0
        )

        # Search

        ctk.CTkLabel(
            self.filter_frame,
            text="Search",
            font=("Segoe UI", 12),
            text_color=COLORS["secondary_text"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 5)
        )

        self.search_entry = ctk.CTkEntry(
            self.filter_frame,
            placeholder_text="Search product name or SKU...",
            height=36
        )

        self.search_entry.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=15,
            pady=(0, 15)
        )

        self.search_entry.bind(
            "<KeyRelease>",
            self.on_search_changed
        )

        # Movement type filter

        ctk.CTkLabel(
            self.filter_frame,
            text="Movement Type",
            font=("Segoe UI", 12),
            text_color=COLORS["secondary_text"]
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=10,
            pady=(12, 5)
        )

        self.type_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=[
                "All Types",
                "Opening",
                "Stock In",
                "Stock Out"
            ],
            command=self.apply_filters,
            height=36,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
            button_hover_color=COLORS["primary_hover"]
        )

        self.type_filter.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=10,
            pady=(0, 15)
        )

        self.type_filter.set("All Types")

        # Product filter

        ctk.CTkLabel(
            self.filter_frame,
            text="Product",
            font=("Segoe UI", 12),
            text_color=COLORS["secondary_text"]
        ).grid(
            row=0,
            column=2,
            sticky="w",
            padx=10,
            pady=(12, 5)
        )

        self.product_filter = ctk.CTkOptionMenu(
            self.filter_frame,
            values=["All Products"],
            command=self.apply_filters,
            height=36,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
            button_hover_color=COLORS["primary_hover"]
        )

        self.product_filter.grid(
            row=1,
            column=2,
            sticky="ew",
            padx=10,
            pady=(0, 15)
        )

        self.product_filter.set("All Products")

        # Refresh button

        ctk.CTkButton(
            self.filter_frame,
            text="Refresh",
            command=self.refresh_history,
            height=36,
            width=90
        ).grid(
            row=1,
            column=3,
            padx=15,
            pady=(0, 15)
        )

    # --------------------------------------------------
    # HISTORY TABLE
    # --------------------------------------------------

    def create_history_table(self):

        self.table_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.table_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(10, 20)
        )

        self.table_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.table_frame.grid_rowconfigure(
            1,
            weight=1
        )

        # Table heading

        heading = ctk.CTkFrame(
            self.table_frame,
            fg_color="transparent"
        )

        heading.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=15
        )

        self.result_count_label = ctk.CTkLabel(
            heading,
            text="Loading records...",
            font=("Segoe UI", 13, "bold"),
            text_color=COLORS["text"]
        )

        self.result_count_label.pack(side="left")

        # Scrollable table

        self.history_table = ctk.CTkScrollableFrame(
            self.table_frame,
            fg_color="transparent"
        )

        self.history_table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 15)
        )

        column_weights = [2, 2, 1, 1, 1, 2, 3]

        for column, weight in enumerate(column_weights):
            self.history_table.grid_columnconfigure(
                column,
                weight=weight
            )

    # --------------------------------------------------
    # LOAD FILTER OPTIONS
    # --------------------------------------------------

    def load_filter_options(self):

        try:

            self.products = get_all_products(
                include_archived=True
            )

            self.product_filter_options = {
                "All Products": None
            }

            for product in self.products:

                display_name = (
                    f"{product['name']} ({product['sku']})"
                )

                self.product_filter_options[display_name] = (
                    product["id"]
                )

            options = list(
                self.product_filter_options.keys()
            )

            self.product_filter.configure(
                values=options
            )

            self.product_filter.set("All Products")

        except Exception as error:

            messagebox.showerror(
                "Filter Loading Error",
                f"Could not load products:\n{error}"
            )

    # --------------------------------------------------
    # LOAD HISTORY
    # --------------------------------------------------

    def load_history(self):

        try:

            # Retrieve up to 10,000 recent movements.
            self.movements = get_stock_movements(
                limit=10000
            )

            self.apply_filters()

        except Exception as error:

            messagebox.showerror(
                "History Loading Error",
                f"Could not load stock history:\n{error}"
            )

    # --------------------------------------------------
    # SEARCH EVENT
    # --------------------------------------------------

    def on_search_changed(self, event=None):

        self.apply_filters()

    # --------------------------------------------------
    # APPLY FILTERS
    # --------------------------------------------------

    def apply_filters(self, selected_value=None):

        search_text = (
            self.search_entry.get().strip().casefold()
        )

        selected_type = self.type_filter.get()
        selected_product = self.product_filter.get()

        filtered_movements = []

        for movement in self.movements:

            # Search by product name or SKU.

            product_name = movement["product_name"].casefold()
            product_sku = movement["product_sku"].casefold()

            if search_text:
                if (
                    search_text not in product_name
                    and search_text not in product_sku
                ):
                    continue

            # Filter by movement type.

            if selected_type == "Opening":
                if movement["movement_type"] != "OPENING":
                    continue

            elif selected_type == "Stock In":
                if movement["movement_type"] != "STOCK_IN":
                    continue

            elif selected_type == "Stock Out":
                if movement["movement_type"] != "STOCK_OUT":
                    continue

            # Filter by product.

            selected_product_id = (
                self.product_filter_options.get(selected_product)
            )

            if selected_product_id is not None:
                if movement["product_id"] != selected_product_id:
                    continue

            filtered_movements.append(movement)

        self.display_movements(filtered_movements)

    # --------------------------------------------------
    # DISPLAY MOVEMENTS
    # --------------------------------------------------

    def display_movements(self, movements):

        # Remove previous table rows.

        for widget in self.history_table.winfo_children():
            widget.destroy()

        self.result_count_label.configure(
            text=f"{len(movements)} movement(s) found"
        )

        headers = [
            "DATE & TIME",
            "PRODUCT",
            "SKU",
            "TYPE",
            "QUANTITY",
            "STOCK AFTER",
            "REASON"
        ]

        for column, header in enumerate(headers):

            ctk.CTkLabel(
                self.history_table,
                text=header,
                font=("Segoe UI", 11, "bold"),
                text_color=COLORS["secondary_text"],
                anchor="w"
            ).grid(
                row=0,
                column=column,
                sticky="w",
                padx=8,
                pady=10
            )

        if not movements:

            ctk.CTkLabel(
                self.history_table,
                text="No stock movements match your filters.",
                font=("Segoe UI", 13),
                text_color=COLORS["muted_text"]
            ).grid(
                row=1,
                column=0,
                columnspan=7,
                pady=35
            )

            return

        for row_number, movement in enumerate(
            movements,
            start=1
        ):

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

            date_text = (
                movement["created_at"]
                .replace("T", " ")[:19]
            )

            reason = movement["reason"] or "—"

            values = [
                date_text,
                movement["product_name"],
                movement["product_sku"],
                type_text,
                quantity_text,
                str(movement["stock_after"]),
                reason
            ]

            for column, value in enumerate(values):

                if column == 3:
                    text_color = type_color

                elif column == 4:
                    text_color = type_color

                else:
                    text_color = COLORS["text"]

                ctk.CTkLabel(
                    self.history_table,
                    text=value,
                    font=("Segoe UI", 11),
                    text_color=text_color,
                    anchor="w"
                ).grid(
                    row=row_number,
                    column=column,
                    sticky="w",
                    padx=8,
                    pady=9
                )

    # --------------------------------------------------
    # REFRESH HISTORY
    # --------------------------------------------------

    def refresh_history(self):

        self.load_filter_options()
        self.load_history()
