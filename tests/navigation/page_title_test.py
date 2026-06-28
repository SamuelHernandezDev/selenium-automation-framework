#tests\navigation\page_title_test.py

"""
Verify that the application title is displayed correctly.
"""

from pages.home_page import HomePage
from tests.base_test import BaseTest


class PageTitleTest(BaseTest):

    def execute(self):

        home = HomePage(self.driver)

        home.open()

        print({
            "title": home.get_title()
        })


if __name__ == "__main__":

    test = PageTitleTest()

    test.execute()

    test.teardown()