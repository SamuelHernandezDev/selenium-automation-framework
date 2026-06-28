#tests\navigation\redirect_test.py

"""
Verify the redirect navigation flow.
"""

from pages.home_page import HomePage
from tests.base_test import BaseTest


class RedirectTest(BaseTest):

    def execute(self):

        home = HomePage(self.driver)

        home.open()

        redirect = home.go_to_redirect()

        print({
            "redirect_heading": redirect.get_heading()
        })


if __name__ == "__main__":

    test = RedirectTest()

    test.execute()

    test.teardown()