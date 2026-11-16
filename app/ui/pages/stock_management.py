
import customtkinter as ctk
from tkinter import messagebox

from app.services.product_service import get_all_products
from app.services.stock_service import (
    stock_in,
    stock_out,
    get_stock_movements
)
from app.ui.theme import COLORS


class StockManagementPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["background"]
        )

        self.product_options = {}
        self.selected_product = None
        self.movement_type = "STOCK_IN"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.create_page_heading()
        self.create_stock_form()
        self.create_history_section()

        self.load_products()
        self.load_movements()

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
            text="Stock Management",
            font=("Segoe UI", 24, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            heading,
            text="Manage incoming and outgoing product stock.",
            font=("Segoe UI", 13),
            text_color=COLORS["secondary_text"]
        ).pack(anchor="w", pady=(4, 0))

    # --------------------------------------------------
    # STOCK FORM
    # --------------------------------------------------

    def create_stock_form(self):

        self.form_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.form_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=25,
            pady=10
        )

        self.form_frame.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        ctk.CTkLabel(
            self.form_frame,
            text="Record Stock Movement",
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            padx=20,
            pady=(20, 15)
        )

        # Product selection

        ctk.CTkLabel(
            self.form_frame,
            text="Select Product",
            text_color=COLORS["secondary_text"],
            font=("Segoe UI", 12)
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
            pady=(5, 5)
        )

        self.product_menu = ctk.CTkOptionMenu(
            self.form_frame,
            values=["Loading products..."],
            command=self.on_product_selected,
            height=38,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
            button_hover_color=COLORS["primary_hover"]
        )

        self.product_menu.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 15)
        )

        # Current stock display

        ctk.CTkLabel(
            self.form_frame,
            text="Current Stock",
            text_color=COLORS["secondary_text"],
            font=("Segoe UI", 12)
        ).grid(
            row=1,
            column=1,
            sticky="w",
            padx=20,
            pady=(5, 5)
        )

        self.current_stock_label = ctk.CTkLabel(
            self.form_frame,
            text="—",
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["text"],
            fg_color=COLORS["background"],
            corner_radius=8,
            height=38
        )

        self.current_stock_label.grid(
            row=2,
            column=1,
            sticky="ew",
            padx=20,
            pady=(0, 15)
        )

        # Movement type

        ctk.CTkLabel(
            self.form_frame,
            text="Movement Type",
            text_color=COLORS["secondary_text"],
            font=("Segoe UI", 12)
        ).grid(
            row=3,
            column=0,
            sticky="w",
            padx=20,
            pady=(5, 5)
        )

        self.movement_selector = ctk.CTkSegmentedButton(
            self.form_frame,
            values=["Stock In", "Stock Out"],
            command=self.on_movement_type_changed,
            selected_color=COLORS["primary"],
            selected_hover_color=COLORS["primary_hover"],
            height=38
        )

        self.movement_selector.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=20,
            pady=(0, 15)
        )

        self.movement_selector.set("Stock In")

        # Quantity

        ctk.CTkLabel(
            self.form_frame,
            text="Quantity",
            text_color=COLORS["secondary_text"],
            font=("Segoe UI", 12)
        ).grid(
            row=3,
            column=1,
            sticky="w",
            padx=20,
            pady=(5, 5)
        )

        self.quantity_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="Enter quantity",
            height=38
        )

        self.quantity_entry.grid(
            row=4,
            column=1,
            sticky="ew",
            padx=20,
            pady=(0, 15)
        )

        # Reason

        ctk.CTkLabel(
            self.form_frame,
            text="Reason",
            text_color=COLORS["secondary_text"],
            font=("Segoe UI", 12)
        ).grid(
            row=5,
            column=0,
            sticky="w",
            padx=20,
            pady=(5, 5)
        )

        self.reason_entry = ctk.CTkEntry(
            self.form_frame,
            placeholder_text="e.g. New shipment, damaged items",
            height=38
        )

        self.reason_entry.grid(
            row=6,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(0, 15)
        )

        # Submit button

        self.submit_button = ctk.CTkButton(
            self.form_frame,
            text="Record Stock In",
            command=self.submit_stock_movement,
            height=40,
            font=("Segoe UI", 13, "bold"),
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"]
        )

        self.submit_button.grid(
            row=7,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(0, 20)
        )

    # --------------------------------------------------
    # STOCK HISTORY SECTION
    # --------------------------------------------------

    def create_history_section(self):

        self.history_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.history_frame.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=25,
            pady=(10, 20)
        )

        self.history_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.history_frame.grid_rowconfigure(
            1,
            weight=1
        )

        # History heading

        heading = ctk.CTkFrame(
            self.history_frame,
            fg_color="transparent"
        )

        heading.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=20,
            pady=15
        )

        ctk.CTkLabel(
            heading,
            text="Recent Stock Movements",
            font=("Segoe UI", 17, "bold"),
            text_color=COLORS["text"]
        ).pack(side="left")

        ctk.CTkButton(
            heading,
            text="Refresh",
            width=90,
            height=32,
            command=self.load_movements
        ).pack(side="right")

        # Scrollable history table

        self.history_table = ctk.CTkScrollableFrame(
            self.history_frame,
            fg_color="transparent"
        )

        self.history_table.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=(0, 15)
        )

        self.history_table.grid_columnconfigure(
            (0, 1, 2, 3, 4, 5),
            weight=1
        )

    # --------------------------------------------------
    # LOAD PRODUCTS
    # --------------------------------------------------

    def load_products(self):

        try:
            products = get_all_products()

            self.product_options.clear()

            for product in products:

                display_name = (
                    f"{product['name']} ({product['sku']})"
                )

                self.product_options[display_name] = product

            options = list(self.product_options.keys())

            if not options:

                self.product_menu.configure(
                    values=["No active products"],
                    state="disabled"
                )

                self.current_stock_label.configure(
                    text="No products available"
                )

                self.selected_product = None
                self.submit_button.configure(state="disabled")

                return

            self.product_menu.configure(
                values=options,
                state="normal"
            )

            self.product_menu.set(options[0])

            self.on_product_selected(options[0])

            self.submit_button.configure(state="normal")

        except Exception as error:

            messagebox.showerror(
                "Product Loading Error",
                f"Could not load products:\n{error}"
            )

    # --------------------------------------------------
    # PRODUCT SELECTION
    # --------------------------------------------------

    def on_product_selected(self, selected_name):

        product = self.product_options.get(selected_name)

        if product is None:
            return

        self.selected_product = product

        self.current_stock_label.configure(
            text=str(product["quantity"])
        )

    # --------------------------------------------------
    # MOVEMENT TYPE SELECTION
    # --------------------------------------------------

    def on_movement_type_changed(self, selected_type):

        if selected_type == "Stock In":

            self.movement_type = "STOCK_IN"

            self.submit_button.configure(
                text="Record Stock In",
                fg_color=COLORS["primary"]
            )

        else:

            self.movement_type = "STOCK_OUT"

            self.submit_button.configure(
                text="Record Stock Out",
                fg_color=COLORS["danger"]
            )

    # --------------------------------------------------
    # SUBMIT STOCK MOVEMENT
    # --------------------------------------------------

    def submit_stock_movement(self):

        if self.selected_product is None:

            messagebox.showwarning(
                "Product Required",
                "Please select a product."
            )

            return

        quantity_text = self.quantity_entry.get().strip()

        if not quantity_text.isdigit():

            messagebox.showwarning(
                "Invalid Quantity",
                "Please enter a valid whole number."
            )

            return

        quantity = int(quantity_text)

        if quantity <= 0:

            messagebox.showwarning(
                "Invalid Quantity",
                "Quantity must be greater than zero."
            )

            return

        reason = self.reason_entry.get().strip()

        product_id = self.selected_product["id"]

        try:

            if self.movement_type == "STOCK_IN":

                new_quantity = stock_in(
                    product_id,
                    quantity,
                    reason
                )

                success_message = (
                    f"Stock added successfully.\n\n"
                    f"New stock quantity: {new_quantity}"
                )

            else:

                new_quantity = stock_out(
                    product_id,
                    quantity,
                    reason
                )

                success_message = (
                    f"Stock removed successfully.\n\n"
                    f"Remaining stock: {new_quantity}"
                )

            messagebox.showinfo(
                "Stock Updated",
                success_message
            )

            # Clear the input fields.
            self.quantity_entry.delete(0, "end")
            self.reason_entry.delete(0, "end")

            # Refresh product stock and movement history.
            self.load_products()
            self.load_movements()

        except ValueError as error:

            messagebox.showwarning(
                "Stock Movement Failed",
                str(error)
            )

        except Exception as error:

            messagebox.showerror(
                "Unexpected Error",
                f"Could not update stock:\n{error}"
            )

    # --------------------------------------------------
    # LOAD MOVEMENT HISTORY
    # --------------------------------------------------

    def load_movements(self):

        try:

            movements = get_stock_movements(limit=100)

            # Remove the previous table contents.
            for widget in self.history_table.winfo_children():
                widget.destroy()

            headers = [
                "PRODUCT",
                "SKU",
                "TYPE",
                "QUANTITY",
                "STOCK AFTER",
                "DATE"
            ]

            for column, header in enumerate(headers):

                ctk.CTkLabel(
                    self.history_table,
                    text=header,
                    font=("Segoe UI", 11, "bold"),
                    text_color=COLORS["secondary_text"]
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
                    text="No stock movements recorded yet.",
                    font=("Segoe UI", 13),
                    text_color=COLORS["muted_text"]
                ).grid(
                    row=1,
                    column=0,
                    columnspan=6,
                    pady=30
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

                elif movement_type == "STOCK_OUT":
                    type_text = "Stock Out"
                    type_color = COLORS["danger"]

                else:
                    type_text = "Opening"
                    type_color = COLORS["primary"]

                date_text = (
                    movement["created_at"]
                    .replace("T", " ")[:19]
                )

                values = [
                    movement["product_name"],
                    movement["product_sku"],
                    type_text,
                    str(movement["quantity"]),
                    str(movement["stock_after"]),
                    date_text
                ]

                for column, value in enumerate(values):

                    text_color = (
                        type_color
                        if column == 2
                        else COLORS["text"]
                    )

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

        except Exception as error:

            messagebox.showerror(
                "History Loading Error",
                f"Could not load stock history:\n{error}"
            )
