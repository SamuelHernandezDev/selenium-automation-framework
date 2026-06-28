# utils/driver.py

"""
WebDriver factory.

Creates and configures a Chrome WebDriver instance
used throughout the automation framework.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager

from config.settings import HEADLESS


def create_driver():
    """
    Create and configure a Chrome WebDriver.
    """

    options = Options()

    if HEADLESS:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    return webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options,
    )