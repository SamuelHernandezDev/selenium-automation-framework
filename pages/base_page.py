"""
Base Page Object.

Provides common browser interactions and helper methods
shared across every page object.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    """
    Base class for all Page Objects.
    """

    def __init__(
        self,
        driver,
        timeout: int = 30,
    ):

        self.driver = driver

        self.wait = WebDriverWait(
            driver,
            timeout,
        )

    # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def visit(self, url: str) -> None:
        """
        Navigate to the specified URL.
        """

        self.driver.get(url)

    # --------------------------------------------------
    # Actions
    # --------------------------------------------------

    def click(self, by: By, value: str) -> None:
        """
        Wait until an element becomes clickable
        and perform a click.
        """

        self.wait_clickable(
            by,
            value,
        ).click()

    # --------------------------------------------------
    # Wait Helpers
    # --------------------------------------------------

    def wait_visible(self, by: By, value: str):
        """
        Wait until an element becomes visible.
        """

        return self.wait.until(
            EC.visibility_of_element_located(
                (by, value)
            )
        )

    def wait_clickable(self, by: By, value: str):
        """
        Wait until an element becomes clickable.
        """

        return self.wait.until(
            EC.element_to_be_clickable(
                (by, value)
            )
        )

    def wait_all_present(self, by: By, value: str):
        """
        Wait until all matching elements are present.
        """

        return self.wait.until(
            EC.presence_of_all_elements_located(
                (by, value)
            )
        )

    def get_text(self, by: By, value: str) -> str:
        """
        Wait until an element is visible
        and return its text.
        """

        return self.wait_visible(
            by,
            value,
        ).text

    # --------------------------------------------------
    # Browser
    # --------------------------------------------------

    def switch_to_last_window(self) -> None:
        """
        Switch focus to the newest browser window.
        """

        if len(self.driver.window_handles) > 1:

            self.driver.switch_to.window(
                self.driver.window_handles[-1]
            )

    def get_title(self) -> str:
        """
        Return the current page title.
        """

        return self.driver.title
