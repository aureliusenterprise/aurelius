import re

from playwright.sync_api import Page, expect


def test__main_page_has_welcome_message(base_url: str, authenticated: Page) -> None:
    """
    Test that the main page has a welcome message.

    Asserts:
        - The page loads successfully.
        - The welcome message is visible on the page.
    """
    authenticated.goto(base_url)

    expect(authenticated.get_by_text(re.compile("Welcome"))).to_be_visible()
