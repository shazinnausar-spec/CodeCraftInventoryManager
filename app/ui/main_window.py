
# Import CustomTkinter.
import customtkinter as ctk

# Import application information.
from app.config import APP_NAME, APP_VERSION

# Import theme settings.
from app.ui.theme import (
    COLORS,
    FONT_FAMILY,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    MIN_WINDOW_HEIGHT
)

# Import reusable components.
from app.ui.components.sidebar import Sidebar
from app.ui.components.header import Header

# Import application pages.
from app.ui.pages.dashboard import DashboardPage
from app.ui.pages.products import ProductsPage
from app.ui.pages.categories import CategoriesPage
from app.ui.pages.stock_management import StockManagementPage
from app.ui.pages.stock_history import StockHistoryPage
from app.ui.pages.reports import ReportsPage
from app.ui.pages.backup import BackupPage
from app.ui.pages.settings import SettingsPage
from app.ui.pages.about import AboutPage


class MainWindow(ctk.CTk):

    def __init__(self):

        # Set appearance before creating the window.
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # Initialize the main window.
        super().__init__()

        # Configure window title.
        self.title(
            f"{APP_NAME} | Version {APP_VERSION}"
        )

        # Configure window size.
        self.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
        )

        # Configure minimum window size.
        self.minsize(
            MIN_WINDOW_WIDTH,
            MIN_WINDOW_HEIGHT
        )

        # Configure background.
        self.configure(
            fg_color=COLORS["background"]
        )

        # Configure main layout.
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Register application pages.
        self.pages = {
            "dashboard": DashboardPage,
            "products": ProductsPage,
            "categories": CategoriesPage,
            "stock_management": StockManagementPage,
            "stock_history": StockHistoryPage,
            "reports": ReportsPage,
            "backup": BackupPage,
            "settings": SettingsPage,
            "about": AboutPage
        }

        # Store page titles.
        self.page_titles = {
            "dashboard": "Dashboard",
            "products": "Products",
            "categories": "Categories",
            "stock_management": "Stock Management",
            "stock_history": "Stock History",
            "reports": "Reports",
            "backup": "Backup & Restore",
            "settings": "Settings",
            "about": "About"
        }

        # Create interface components.
        self.create_sidebar()
        self.create_workspace()

        # Open the initial dashboard.
        self.show_page("dashboard")

    def create_sidebar(self):

        # Create sidebar.
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_page
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

    def create_workspace(self):

        # Create main workspace container.
        self.workspace = ctk.CTkFrame(
            self,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        self.workspace.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        # Allow workspace to expand.
        self.workspace.grid_columnconfigure(
            0,
            weight=1
        )

        self.workspace.grid_rowconfigure(
            1,
            weight=1
        )

        # Create application header.
        self.header = Header(
            self.workspace
        )

        self.header.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        # Create page container.
        self.page_container = ctk.CTkFrame(
            self.workspace,
            fg_color=COLORS["background"],
            corner_radius=0
        )

        self.page_container.grid(
            row=1,
            column=0,
            sticky="nsew"
        )

        # Allow page content to expand.
        self.page_container.grid_columnconfigure(
            0,
            weight=1
        )

        self.page_container.grid_rowconfigure(
            0,
            weight=1
        )

    def show_page(self, page_id):
        """Display the selected application page."""

        # Get the selected page class.
        page_class = self.pages.get(page_id)

        # Ignore unknown page identifiers.
        if page_class is None:
            return

        # Update the application header.
        self.header.set_title(
            self.page_titles[page_id]
        )

        # Remove the previous page.
        for widget in self.page_container.winfo_children():
            widget.destroy()

        # Create the selected page.
        page = page_class(
            self.page_container
        )

        # Display the page.
        page.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
