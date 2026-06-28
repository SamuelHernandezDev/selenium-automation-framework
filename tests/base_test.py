# tests/base_test.py

"""
Base Test.

Provides the browser lifecycle shared by
all Selenium automation tests.
"""

from utils.driver import create_driver


class BaseTest:
    """
    Base class for Selenium test cases.
    """

    def __init__(self):
        self.driver = create_driver()

    def teardown(self):
        """
        Close the browser.
        """
        self.driver.quit()