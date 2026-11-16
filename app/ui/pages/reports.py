
# Import CustomTkinter.
import customtkinter as ctk

# Import file dialog and message boxes.
from tkinter import filedialog, messagebox

# Import application theme.
from app.ui.theme import COLORS, FONT_FAMILY

# Import export directory.
from app.config import EXPORT_DIR

# Import report services.
from app.services.reports_service import (
    get_inventory_report,
    get_low_stock_report,
    get_stock_movement_report,
    export_report_to_csv
)


class ReportsPage(ctk.CTkFrame):

    def __init__(self, parent):

        super().__init__(
            parent,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        self.pack_propagate(False)

        # Store the current report records.
        self.report_rows = []

        # Define available reports and their columns.
        self.report_definitions = {

            "Inventory Report": {
                "type": "inventory",
                "columns": [
                    ("Product", "name"),
                    ("SKU", "sku"),
                    ("Category", "category_name"),
                    ("Purchase Price", "purchase_price_cents"),
                    ("Selling Price", "selling_price_cents"),
                    ("Quantity", "quantity"),
                    ("Minimum", "minimum_stock"),
                    ("Inventory Value", "inventory_value_cents"),
                    ("Status", "status"),
                ]
            },

            "Low Stock Report": {
                "type": "low_stock",
                "columns": [
                    ("Product", "name"),
                    ("SKU", "sku"),
                    ("Category", "category_name"),
                    ("Current Stock", "quantity"),
                    ("Minimum Stock", "minimum_stock"),
                    ("Purchase Price", "purchase_price_cents"),
                    ("Selling Price", "selling_price_cents"),
                ]
            },

            "Stock Movement Report": {
                "type": "stock_movements",
                "columns": [
                    ("Date", "created_at"),
                    ("Product", "product_name"),
                    ("SKU", "product_sku"),
                    ("Movement", "movement_type"),
                    ("Quantity", "quantity"),
                    ("Stock After", "stock_after"),
                    ("Reason", "reason"),
                ]
            }

        }

        self.create_header()
        self.create_report_controls()
        self.create_report_summary()
        self.create_report_table()

        # Load the initial report.
        self.load_report("Inventory Report")

    # --------------------------------------------------
    # PAGE HEADER
    # --------------------------------------------------

    def create_header(self):

        ctk.CTkLabel(
            self,
            text="Reports & Exports",
            font=(FONT_FAMILY, 25, "bold"),
            text_color=COLORS["text"]
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 5)
        )

        ctk.CTkLabel(
            self,
            text="Review inventory information and export business reports.",
            font=(FONT_FAMILY, 13),
            text_color=COLORS["secondary_text"]
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

    # --------------------------------------------------
    # REPORT CONTROLS
    # --------------------------------------------------

    def create_report_controls(self):

        controls = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        controls.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        controls.grid_columnconfigure(0, weight=1)

        # Report selection.
        ctk.CTkLabel(
            controls,
            text="Select Report",
            font=(FONT_FAMILY, 12, "bold"),
            text_color=COLORS["text"]
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=15,
            pady=(12, 5)
        )

        self.report_selector = ctk.CTkOptionMenu(
            controls,
            values=list(self.report_definitions.keys()),
            width=230,
            height=36,
            command=self.load_report,
            fg_color=COLORS["primary"],
            button_color=COLORS["primary_hover"],
            button_hover_color=COLORS["primary_hover"]
        )

        self.report_selector.grid(
            row=1,
            column=0,
            sticky="w",
            padx=15,
            pady=(0, 12)
        )

        # Refresh button.
        ctk.CTkButton(
            controls,
            text="Refresh",
            width=100,
            height=36,
            command=self.refresh_report,
            fg_color=COLORS["sidebar_hover"],
            hover_color=COLORS["sidebar"]
        ).grid(
            row=1,
            column=1,
            padx=5,
            pady=(0, 12)
        )

        # Export button.
        ctk.CTkButton(
            controls,
            text="Export CSV",
            width=120,
            height=36,
            command=self.export_current_report
        ).grid(
            row=1,
            column=2,
            padx=(5, 15),
            pady=(0, 12)
        )

    # --------------------------------------------------
    # REPORT SUMMARY
    # --------------------------------------------------

    def create_report_summary(self):

        self.summary_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=10,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.summary_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        self.summary_label = ctk.CTkLabel(
            self.summary_frame,
            text="Loading report...",
            font=(FONT_FAMILY, 12),
            text_color=COLORS["secondary_text"]
        )

        self.summary_label.pack(
            anchor="w",
            padx=15,
            pady=12
        )

    # --------------------------------------------------
    # REPORT TABLE
    # --------------------------------------------------

    def create_report_table(self):

        self.table_panel = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=12,
            border_width=1,
            border_color=COLORS["border"]
        )

        self.table_panel.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 25)
        )

        self.table_title = ctk.CTkLabel(
            self.table_panel,
            text="Report Preview",
            font=(FONT_FAMILY, 16, "bold"),
            text_color=COLORS["text"]
        )

        self.table_title.pack(
            anchor="w",
            padx=15,
            pady=15
        )

        # Scrollable table area.
        self.table_container = ctk.CTkScrollableFrame(
            self.table_panel,
            fg_color=COLORS["card"],
            corner_radius=0
        )

        self.table_container.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

    # --------------------------------------------------
    # LOAD REPORT
    # --------------------------------------------------

    def load_report(self, report_name):

        try:

            if report_name == "Inventory Report":

                rows = get_inventory_report()

            elif report_name == "Low Stock Report":

                rows = get_low_stock_report()

            elif report_name == "Stock Movement Report":

                rows = get_stock_movement_report()

            else:

                raise ValueError("Unknown report selected.")

            # Store current report.
            self.report_rows = rows
            self.current_report_name = report_name

            # Update report summary.
            self.summary_label.configure(
                text=f"Total records: {len(rows):,}"
            )

            # Update table heading.
            self.table_title.configure(
                text=f"{report_name} - Preview"
            )

            # Display report records.
            self.display_report(rows, report_name)

        except Exception as error:

            messagebox.showerror(
                "Report Error",
                f"Could not load report:\n{error}"
            )

    # --------------------------------------------------
    # DISPLAY REPORT
    # --------------------------------------------------

    def display_report(self, rows, report_name):

        # Clear the previous table.
        for widget in self.table_container.winfo_children():
            widget.destroy()

        definition = self.report_definitions[report_name]

        columns = definition["columns"]

        # Configure table columns.
        self.table_container.grid_columnconfigure(
            tuple(range(len(columns))),
            weight=1
        )

        # Create table header.
        for column_index, (heading, key) in enumerate(columns):

            header = ctk.CTkLabel(
                self.table_container,
                text=heading,
                font=(FONT_FAMILY, 11, "bold"),
                text_color=COLORS["text"],
                fg_color=COLORS["background"],
                corner_radius=4,
                anchor="w"
            )

            header.grid(
                row=0,
                column=column_index,
                sticky="ew",
                padx=2,
                pady=3
            )

        if not rows:

            empty_message = ctk.CTkLabel(
                self.table_container,
                text="No records found for this report.",
                font=(FONT_FAMILY, 13),
                text_color=COLORS["muted_text"]
            )

            empty_message.grid(
                row=1,
                column=0,
                columnspan=len(columns),
                padx=15,
                pady=30
            )

            return

        # Display each report record.
        for row_index, record in enumerate(rows, start=1):

            background = (
                COLORS["background"]
                if row_index % 2 == 0
                else COLORS["card"]
            )

            for column_index, (heading, key) in enumerate(columns):

                value = record.get(key, "")

                # Format monetary values.
                if key in (
                    "purchase_price_cents",
                    "selling_price_cents",
                    "inventory_value_cents"
                ):

                    value = f"LKR {value / 100:,.2f}"

                # Format movement names.
                elif key == "movement_type":

                    value = value.replace("_", " ").title()

                # Keep date display readable.
                elif key == "created_at" and value:

                    value = str(value).replace("T", " ")

                # Display blank values safely.
                if value is None or value == "":
                    value = "—"

                cell = ctk.CTkLabel(
                    self.table_container,
                    text=str(value),
                    font=(FONT_FAMILY, 10),
                    text_color=COLORS["text"],
                    fg_color=background,
                    anchor="w",
                    justify="left",
                    wraplength=160
                )

                cell.grid(
                    row=row_index,
                    column=column_index,
                    sticky="ew",
                    padx=2,
                    pady=2
                )

    # --------------------------------------------------
    # REFRESH REPORT
    # --------------------------------------------------

    def refresh_report(self):

        self.load_report(
            self.report_selector.get()
        )

    # --------------------------------------------------
    # EXPORT REPORT
    # --------------------------------------------------

    def export_current_report(self):

        if not self.report_rows:

            messagebox.showinfo(
                "No Records",
                "There are no records available to export."
            )

            return

        # Ask user to choose an export folder.
        selected_folder = filedialog.askdirectory(
            title="Choose CSV Export Folder",
            initialdir=str(EXPORT_DIR),
            mustexist=True
        )

        if not selected_folder:
            return

        try:

            report_type = self.report_definitions[
                self.current_report_name
            ]["type"]

            # Export CSV.
            file_path = export_report_to_csv(
                report_type,
                self.report_rows,
                selected_folder
            )

            messagebox.showinfo(
                "Export Successful",
                f"Report exported successfully!\n\n{file_path}"
            )

        except Exception as error:

            messagebox.showerror(
                "Export Error",
                f"Could not export report:\n{error}"
            )
