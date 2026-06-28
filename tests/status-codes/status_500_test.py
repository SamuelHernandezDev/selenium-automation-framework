#tests\status-codes\status_500_test.py

"""
Verify the HTTP 500 status page.
"""

from pages.home_page import HomePage
from tests.base_test import BaseTest


class Status500Test(BaseTest):

    def execute(self):

        home = HomePage(self.driver)

        home.open()

        status_codes = (
            home
            .go_to_redirect()
            .go_to_status_codes()
        )

        status_codes.open_code("500")

        print({
            "message": status_codes.get_message()
        })


if __name__ == "__main__":

    test = Status500Test()

    test.execute()

    test.teardown()