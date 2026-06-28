# pages/home_page.py

"""
Home Page Object.

Represents the application's home page and provides
the available interactions from the landing page.
"""

from selenium.webdriver.common.by import By

from config.settings import BASE_URL

from pages.base_page import BasePage
from pages.redirect_page import RedirectPage


class HomePage(BasePage):
    """
    Page Object for the application's home page.
    """

    # --------------------------------------------------
    # Locators
    # --------------------------------------------------

    REDIRECT_LINK = (
        By.LINK_TEXT,
        "Redirect Link",
    )

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def open(self):
        """
        Open the application's home page.
        """

        self.visit(BASE_URL)

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def go_to_redirect(self):
        """
        Navigate to the Redirect page.

        Returns
        -------
        RedirectPage
            Redirect page object.
        """

        self.click(
            *self.REDIRECT_LINK
        )

        return RedirectPage(self.driver)