#tests\status-codes\list_codes_test.py

"""
Retrieve every available HTTP status code.
"""

from pages.home_page import HomePage
from tests.base_test import BaseTest


class StatusCodesTest(BaseTest):

    def execute(self):

        home = HomePage(self.driver)

        home.open()

        status_codes = (
            home
            .go_to_redirect()
            .go_to_status_codes()
        )

        print({
            "codes": status_codes.get_codes()
        })


if __name__ == "__main__":

    test = StatusCodesTest()

    test.execute()

    test.teardown()