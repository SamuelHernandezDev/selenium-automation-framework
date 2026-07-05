"""
Unit tests for Page Object behavior that does not require a browser.
"""

from pages.base_page import BasePage


class FakeDriver:
    """
    Minimal driver double for Page Object unit tests.
    """

    title = "Demo Title"
    window_handles = ["main"]

    def __init__(self):
        self.visited_url = None

    def get(self, url):
        self.visited_url = url


def test_base_page_visit_delegates_to_driver_get():
    driver = FakeDriver()
    page = BasePage(
        driver,
        timeout=1,
    )

    page.visit("https://example.com")

    assert driver.visited_url == "https://example.com"


def test_base_page_get_title_reads_driver_title():
    page = BasePage(
        FakeDriver(),
        timeout=1,
    )

    assert page.get_title() == "Demo Title"
