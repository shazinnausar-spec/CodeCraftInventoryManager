import customtkinter as ctk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation

from app.services.product_service import (
    get_all_products,
    create_product,
    update_product,
    archive_product
)

from app.services.category_service import get_all_categories

from app.ui.theme import (
    COLORS,
    FONT_FAMILY,
    FONT_SIZE_NORMAL,
    FONT_SIZE_SMALL,
    FONT_SIZE_LARGE
)


class ProductsPage(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        self.categories = []
        self.category_lookup = {}
        self.search_text = ""

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.create_page_header()
        self.create_filter_section()
        self.create_product_table()

        self.load_categories()
        self.load_products()

    def create_page_header(self):
        """Create the page title and Add Product button."""

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
            text="Product Management",
            font=(FONT_FAMILY, 26, "bold"),
            text_color=COLORS["text"]
        )
        title.grid(row=0, column=0, sticky="w")

        description = ctk.CTkLabel(
            header,
            text="Manage your products, prices and stock levels.",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["secondary_text"]
        )
        description.grid(
            row=1,
            column=0,
            sticky="w",
            pady=(5, 0)
        )

        self.add_button = ctk.CTkButton(
            header,
            text="+ Add Product",
            width=140,
            height=38,
            corner_radius=8,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
            command=self.open_add_product_dialog
        )
        self.add_button.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(15, 0)
        )

    def create_filter_section(self):
        """Create the search bar and category filter."""

        filter_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )
        filter_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=30,
            pady=(0, 18)
        )

        filter_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="Search by product name or SKU...",
            height=38,
            width=350,
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

        # Refresh the table whenever the user types.
        self.search_entry.bind(
            "<KeyRelease>",
            self.on_search
        )

        self.category_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All categories"],
            width=190,
            height=38,
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            fg_color=COLORS["primary"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            command=self.on_category_change
        )
        self.category_filter.grid(
            row=0,
            column=1,
            padx=10,
            pady=15
        )

        refresh_button = ctk.CTkButton(
            filter_frame,
            text="Refresh",
            width=90,
            height=38,
            fg_color=COLORS["sidebar"],
            hover_color=COLORS["sidebar_hover"],
            command=self.load_products
        )
        refresh_button.grid(
            row=0,
            column=2,
            padx=(10, 15),
            pady=15
        )

    def create_product_table(self):
        """Create the scrollable product listing."""

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
            text="Product List",
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
        """Load categories into the category filter."""

        try:
            self.categories = get_all_categories()

            self.category_lookup = {
                category["name"]: category["id"]
                for category in self.categories
            }

            category_names = ["All categories"] + [
                category["name"]
                for category in self.categories
            ]

            self.category_filter.configure(
                values=category_names
            )

            self.category_filter.set("All categories")

        except Exception as error:
            messagebox.showerror(
                "Category Error",
                f"Unable to load categories.\n\n{error}"
            )

    def load_products(self):
        """Load products using the current search and filter."""

        try:
            selected_category = self.category_filter.get()

            category_id = self.category_lookup.get(
                selected_category
            )

            products = get_all_products(
                search=self.search_entry.get(),
                category_id=category_id
            )

            self.display_products(products)

        except Exception as error:
            messagebox.showerror(
                "Product Error",
                f"Unable to load products.\n\n{error}"
            )

    def display_products(self, products):
        """Display product records in the table."""

        # Clear previous rows.
        for widget in self.table_scroll.winfo_children():
            widget.destroy()

        # Table column headings.
        headers = [
            "PRODUCT",
            "SKU",
            "CATEGORY",
            "PURCHASE PRICE",
            "SELLING PRICE",
            "STOCK",
            "STATUS",
            "ACTIONS"
        ]

        header_frame = ctk.CTkFrame(
            self.table_scroll,
            fg_color=COLORS["background"],
            corner_radius=6
        )
        header_frame.grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 8)
        )

        column_weights = [3, 2, 2, 2, 2, 1, 2, 2]

        for index, weight in enumerate(column_weights):
            header_frame.grid_columnconfigure(
                index,
                weight=weight
            )

        for index, heading in enumerate(headers):
            label = ctk.CTkLabel(
                header_frame,
                text=heading,
                font=(FONT_FAMILY, FONT_SIZE_SMALL, "bold"),
                text_color=COLORS["secondary_text"],
                anchor="w"
            )
            label.grid(
                row=0,
                column=index,
                sticky="ew",
                padx=8,
                pady=12
            )

        if not products:
            empty_label = ctk.CTkLabel(
                self.table_scroll,
                text="No products found.",
                font=(FONT_FAMILY, FONT_SIZE_MEDIUM),
                text_color=COLORS["secondary_text"]
            )
            empty_label.grid(
                row=1,
                column=0,
                pady=55
            )
            return

        # Display each product.
        for row_index, product in enumerate(products, start=1):

            row_frame = ctk.CTkFrame(
                self.table_scroll,
                fg_color=COLORS["card"],
                corner_radius=5
            )
            row_frame.grid(
                row=row_index,
                column=0,
                sticky="ew",
                pady=3
            )

            for index, weight in enumerate(column_weights):
                row_frame.grid_columnconfigure(
                    index,
                    weight=weight
                )

            purchase_price = (
                product["purchase_price_cents"] / 100
            )

            selling_price = (
                product["selling_price_cents"] / 100
            )

            quantity = product["quantity"]
            minimum_stock = product["minimum_stock"]

            if quantity == 0:
                status = "Out of stock"
                status_color = COLORS["danger"]
            elif quantity <= minimum_stock:
                status = "Low stock"
                status_color = COLORS["warning"]
            else:
                status = "In stock"
                status_color = COLORS["success"]

            values = [
                product["name"],
                product["sku"],
                product["category_name"],
                f"LKR {purchase_price:,.2f}",
                f"LKR {selling_price:,.2f}",
                str(quantity),
                status
            ]

            for column_index, value in enumerate(values):

                text_color = COLORS["text"]

                if column_index == 6:
                    text_color = status_color

                label = ctk.CTkLabel(
                    row_frame,
                    text=value,
                    font=(FONT_FAMILY, FONT_SIZE_SMALL),
                    text_color=text_color,
                    anchor="w"
                )

                label.grid(
                    row=0,
                    column=column_index,
                    sticky="ew",
                    padx=8,
                    pady=13
                )

            # Create the action buttons for this product.
            action_frame = ctk.CTkFrame(
                row_frame,
                fg_color="transparent"
            )
            action_frame.grid(
                row=0,
                column=7,
                sticky="ew",
                padx=4
            )

            edit_button = ctk.CTkButton(
                action_frame,
                text="Edit",
                width=48,
                height=28,
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                fg_color=COLORS["primary"],
                hover_color=COLORS["primary_hover"],
                command=lambda p=product: self.open_edit_product_dialog(p)
            )
            edit_button.pack(
                side="left",
                padx=(0, 4)
            )

            archive_button = ctk.CTkButton(
                action_frame,
                text="Archive",
                width=65,
                height=28,
                font=(FONT_FAMILY, FONT_SIZE_SMALL),
                fg_color=COLORS["danger"],
                hover_color="#B91C1C",
                command=lambda p=product: self.confirm_archive_product(p)
            )
            archive_button.pack(side="left")

    def on_search(self, event=None):
        """Handle product search."""

        self.load_products()

    def on_category_change(self, selected_category):
        """Handle category filter changes."""

        self.load_products()

    def parse_money(self, value, field_name):
        """Convert an LKR amount into integer cents."""

        try:
            amount = Decimal(value.strip())

        except InvalidOperation:
            raise ValueError(
                f"{field_name} must be a valid number."
            )

        if not amount.is_finite():
            raise ValueError(
                f"{field_name} must be a valid number."
            )

        if amount < 0:
            raise ValueError(
                f"{field_name} cannot be negative."
            )

        if amount.as_tuple().exponent < -2:
            raise ValueError(
                f"{field_name} can have a maximum of 2 decimal places."
            )

        return int(amount * 100)

    def open_add_product_dialog(self):
        """Display the form used to create a new product."""

        # A product must belong to an existing category.
        if not self.categories:
            messagebox.showwarning(
                "Category Required",
                "Please create a category before adding a product."
            )
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Product")
        dialog.geometry("550x730")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["background"])

        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)

        # Form heading.
        title = ctk.CTkLabel(
            dialog,
            text="Add New Product",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLORS["text"]
        )
        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=30,
            pady=(25, 5)
        )

        subtitle = ctk.CTkLabel(
            dialog,
            text="Enter the product information below.",
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["secondary_text"]
        )
        subtitle.grid(
            row=1,
            column=0,
            sticky="w",
            padx=30,
            pady=(0, 20)
        )

        # Helper function for creating form labels.
        def add_label(text, row):
            label = ctk.CTkLabel(
                dialog,
                text=text,
                font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                text_color=COLORS["text"]
            )
            label.grid(
                row=row,
                column=0,
                sticky="w",
                padx=30,
                pady=(8, 5)
            )

        # Product name.
        add_label("Product Name *", 2)

        name_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. Wireless Keyboard",
            height=38
        )
        name_entry.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=30
        )

        # SKU.
        add_label("Product SKU *", 4)

        sku_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. KEY-001",
            height=38
        )
        sku_entry.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=30
        )

        # Category.
        add_label("Category *", 6)

        category_names = [
            category["name"]
            for category in self.categories
        ]

        category_menu = ctk.CTkOptionMenu(
            dialog,
            values=category_names,
            height=38,
            width=300
        )
        category_menu.grid(
            row=7,
            column=0,
            sticky="ew",
            padx=30
        )

        category_menu.set(category_names[0])

        # Purchase price.
        add_label("Purchase Price (LKR) *", 8)

        purchase_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. 2500.00",
            height=38
        )
        purchase_entry.grid(
            row=9,
            column=0,
            sticky="ew",
            padx=30
        )

        # Selling price.
        add_label("Selling Price (LKR) *", 10)

        selling_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. 3500.00",
            height=38
        )
        selling_entry.grid(
            row=11,
            column=0,
            sticky="ew",
            padx=30
        )

        # Initial quantity.
        add_label("Opening Stock Quantity *", 12)

        quantity_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. 25",
            height=38
        )
        quantity_entry.grid(
            row=13,
            column=0,
            sticky="ew",
            padx=30
        )

        quantity_entry.insert(0, "0")

        # Minimum stock level.
        add_label("Minimum Stock Level *", 14)

        minimum_entry = ctk.CTkEntry(
            dialog,
            placeholder_text="e.g. 5",
            height=38
        )
        minimum_entry.grid(
            row=15,
            column=0,
            sticky="ew",
            padx=30
        )

        minimum_entry.insert(0, "5")

        # Save the product.
        def save_product():
            name = name_entry.get().strip()
            sku = sku_entry.get().strip()

            selected_category = category_menu.get()
            category_id = self.category_lookup.get(
                selected_category
            )

            try:
                purchase_price = self.parse_money(
                    purchase_entry.get(),
                    "Purchase price"
                )

                selling_price = self.parse_money(
                    selling_entry.get(),
                    "Selling price"
                )

                quantity_text = quantity_entry.get().strip()
                minimum_text = minimum_entry.get().strip()

                if not quantity_text.isdigit():
                    raise ValueError(
                        "Opening stock must be a non-negative whole number."
                    )

                if not minimum_text.isdigit():
                    raise ValueError(
                        "Minimum stock must be a non-negative whole number."
                    )

                quantity = int(quantity_text)
                minimum_stock = int(minimum_text)

                if category_id is None:
                    raise ValueError(
                        "Please select a valid category."
                    )

                # Save through the product service.
                product_id = create_product(
                    name=name,
                    sku=sku,
                    category_id=category_id,
                    purchase_price_cents=purchase_price,
                    selling_price_cents=selling_price,
                    quantity=quantity,
                    minimum_stock=minimum_stock
                )

                messagebox.showinfo(
                    "Product Created",
                    f"{name} was added successfully.",
                    parent=dialog
                )

                dialog.destroy()

                # Refresh the product table.
                self.load_products()

            except ValueError as error:
                messagebox.showwarning(
                    "Invalid Product",
                    str(error),
                    parent=dialog
                )

            except Exception as error:
                messagebox.showerror(
                    "Product Error",
                    f"Unable to create product.\n\n{error}",
                    parent=dialog
                )

        # Form buttons.
        button_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )
        button_frame.grid(
            row=16,
            column=0,
            sticky="e",
            padx=30,
            pady=20
        )

        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            height=38,
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
            text="Save Product",
            width=130,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=save_product
        )
        save_button.pack(side="left")

        name_entry.focus()

    def open_edit_product_dialog(self, product):
        """Open a form to edit existing product details."""

        dialog = ctk.CTkToplevel(self)
        dialog.title("Edit Product")
        dialog.geometry("520x700")
        dialog.resizable(False, False)
        dialog.configure(fg_color=COLORS["background"])

        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            dialog,
            text="Edit Product",
            font=(FONT_FAMILY, 24, "bold"),
            text_color=COLORS["text"]
        )
        title.grid(
            row=0,
            column=0,
            sticky="w",
            padx=30,
            pady=(25, 20)
        )

        def add_label(text, row):
            ctk.CTkLabel(
                dialog,
                text=text,
                font=(FONT_FAMILY, FONT_SIZE_NORMAL, "bold"),
                text_color=COLORS["text"]
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=30,
                pady=(8, 5)
            )

        def add_entry(row, placeholder, value):
            entry = ctk.CTkEntry(
                dialog,
                placeholder_text=placeholder,
                height=38
            )
            entry.grid(
                row=row,
                column=0,
                sticky="ew",
                padx=30
            )
            entry.insert(0, str(value))
            return entry

        add_label("Product Name *", 1)
        name_entry = add_entry(
            2, "Product name", product["name"]
        )

        add_label("Product SKU *", 3)
        sku_entry = add_entry(
            4, "Product SKU", product["sku"]
        )

        add_label("Category *", 5)

        category_names = [
            category["name"]
            for category in self.categories
        ]

        category_menu = ctk.CTkOptionMenu(
            dialog,
            values=category_names,
            height=38
        )
        category_menu.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=30
        )
        category_menu.set(product["category_name"])

        add_label("Purchase Price (LKR) *", 7)
        purchase_entry = add_entry(
            8,
            "Purchase price",
            f'{product["purchase_price_cents"] / 100:.2f}'
        )

        add_label("Selling Price (LKR) *", 9)
        selling_entry = add_entry(
            10,
            "Selling price",
            f'{product["selling_price_cents"] / 100:.2f}'
        )

        # Stock is displayed but cannot be changed here.
        add_label("Current Stock (managed separately)", 11)

        stock_label = ctk.CTkLabel(
            dialog,
            text=str(product["quantity"]),
            font=(FONT_FAMILY, FONT_SIZE_NORMAL),
            text_color=COLORS["secondary_text"]
        )
        stock_label.grid(
            row=12,
            column=0,
            sticky="w",
            padx=30
        )

        add_label("Minimum Stock Level *", 13)
        minimum_entry = add_entry(
            14,
            "Minimum stock",
            product["minimum_stock"]
        )

        def save_changes():
            try:
                name = name_entry.get().strip()
                sku = sku_entry.get().strip()

                category_id = self.category_lookup.get(
                    category_menu.get()
                )

                purchase_price = self.parse_money(
                    purchase_entry.get(),
                    "Purchase price"
                )

                selling_price = self.parse_money(
                    selling_entry.get(),
                    "Selling price"
                )

                minimum_text = minimum_entry.get().strip()

                if not minimum_text.isdigit():
                    raise ValueError(
                        "Minimum stock must be a non-negative whole number."
                    )

                if category_id is None:
                    raise ValueError(
                        "Please select a valid category."
                    )

                update_product(
                    product_id=product["id"],
                    name=name,
                    sku=sku,
                    category_id=category_id,
                    purchase_price_cents=purchase_price,
                    selling_price_cents=selling_price,
                    minimum_stock=int(minimum_text)
                )

                messagebox.showinfo(
                    "Success",
                    "Product updated successfully.",
                    parent=dialog
                )

                dialog.destroy()
                self.load_products()

            except ValueError as error:
                messagebox.showwarning(
                    "Invalid Product",
                    str(error),
                    parent=dialog
                )

            except Exception as error:
                messagebox.showerror(
                    "Update Error",
                    f"Unable to update product.\n\n{error}",
                    parent=dialog
                )

        button_frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )
        button_frame.grid(
            row=15,
            column=0,
            sticky="e",
            padx=30,
            pady=20
        )

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=95,
            height=38,
            fg_color=COLORS["sidebar"],
            hover_color=COLORS["sidebar_hover"],
            command=dialog.destroy
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="Save Changes",
            width=125,
            height=38,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            command=save_changes
        ).pack(side="left")

        name_entry.focus()

    def confirm_archive_product(self, product):
        """Ask for confirmation before archiving a product."""

        confirmed = messagebox.askyesno(
            "Archive Product",
            (
                f'Are you sure you want to archive '
                f'"{product["name"]}"?\n\n'
                "Archived products will no longer appear "
                "in the active product list."
            ),
            parent=self.winfo_toplevel()
        )

        if not confirmed:
            return

        try:
            archive_product(product["id"])

            messagebox.showinfo(
                "Product Archived",
                "The product was archived successfully.",
                parent=self.winfo_toplevel()
            )

            self.load_products()

        except ValueError as error:
            messagebox.showwarning(
                "Cannot Archive Product",
                str(error),
                parent=self.winfo_toplevel()
            )

        except Exception as error:
            messagebox.showerror(
                "Archive Error",
                f"Unable to archive product.\n\n{error}",
                parent=self.winfo_toplevel()
            )