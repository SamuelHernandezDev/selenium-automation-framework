"""
HTTP Status Codes Page Object.

Represents the HTTP Status Codes page and provides
the available interactions with the status code links
and their corresponding detail pages.
"""

from selenium.webdriver.common.by import By

from pages.base_page import BasePage


class StatusCodesPage(BasePage):
    """
    Page Object for the HTTP Status Codes page.
    """

    # --------------------------------------------------
    # Locators
    # --------------------------------------------------

    STATUS_CODES = (
        By.CSS_SELECTOR,
        "ul li a",
    )

    MESSAGE = (
        By.TAG_NAME,
        "p",
    )

    # --------------------------------------------------
    # Information
    # --------------------------------------------------

    def get_codes(self) -> list[str]:
        """
        Return all available HTTP status codes.
        """

        codes = self.wait_all_present(
            *self.STATUS_CODES
        )

        return [
            code.text
            for code in codes
        ]

    def get_message(self) -> str:
        """
        Return the message displayed
        on the current status code page.
        """

        return self.get_text(
            *self.MESSAGE
        )

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def open_code(self, code: str) -> "StatusCodesPage":
        """
        Open the specified HTTP status code page.

        Parameters
        ----------
        code : str
            HTTP status code to open.

        Returns
        -------
        StatusCodesPage
            Current page object.
        """

        codes = self.wait_all_present(
            *self.STATUS_CODES
        )

        for status in codes:

            if status.text == code:

                status.click()

                self.switch_to_last_window()

                return self

        raise ValueError(
            f"Status code '{code}' was not found."
        )
