"""
Redirect Page Object.

Represents the Redirect page and provides
the available interactions for navigating
to the HTTP Status Codes page.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage
from pages.status_codes_page import StatusCodesPage


class RedirectPage(BasePage):
    """
    Page Object for the Redirect page.
    """

    # --------------------------------------------------
    # Locators
    # --------------------------------------------------

    HEADING = (
        By.TAG_NAME,
        "h3",
    )

    REDIRECT_BUTTON = (
        By.ID,
        "redirect",
    )

    # --------------------------------------------------
    # Information
    # --------------------------------------------------

    def get_heading(self) -> str:
        """
        Return the page heading.
        """

        return self.wait_visible(
            *self.HEADING
        ).text

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def go_to_status_codes(self) -> StatusCodesPage:
        """
        Navigate to the HTTP Status Codes page.

        Returns
        -------
        StatusCodesPage
            Status Codes page object.
        """

        self.click(
            *self.REDIRECT_BUTTON
        )

        return StatusCodesPage(self.driver)
