"""
WebDriver factory.

Creates browser instances from framework settings so tests can run
against different profiles without hardcoded driver configuration.
"""

from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from config.settings import BrowserSettings, FrameworkSettings, load_settings


SUPPORTED_BROWSERS = {
    "chrome",
}


class DriverFactory:
    """
    Factory responsible for creating Selenium WebDriver instances.
    """

    def __init__(self, settings: FrameworkSettings | None = None) -> None:
        self.settings = settings or load_settings()

    def create(self):
        """
        Create a WebDriver instance for the configured browser.
        """

        browser_name = self.settings.browser.name.lower()

        if browser_name == "chrome":
            return self._create_chrome(self.settings.browser)

        supported = ", ".join(sorted(SUPPORTED_BROWSERS))
        raise ValueError(
            f"Browser '{browser_name}' is not supported. Supported: {supported}."
        )

    def _create_chrome(self, browser: BrowserSettings):
        """
        Create and configure Chrome WebDriver.
        """

        options = ChromeOptions()

        if browser.headless:
            options.add_argument("--headless=new")

        for argument in browser.arguments:
            options.add_argument(argument)

        driver = webdriver.Chrome(
            service=ChromeService(
                ChromeDriverManager().install()
            ),
            options=options,
        )

        driver.set_window_size(
            browser.window_width,
            browser.window_height,
        )
        driver.set_page_load_timeout(browser.timeout)

        return driver


def create_driver(settings: FrameworkSettings | None = None):
    """
    Convenience wrapper for creating a configured WebDriver.
    """

    return DriverFactory(settings).create()
