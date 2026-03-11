import pytest

BASE_URL = "https://pantuniestal.com"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "pl-PL",
    }


@pytest.fixture()
def page(page):
    page.set_default_timeout(15000)
    yield page


def _accept_cookies(page):
    """Zamknij baner cookies jeśli jest widoczny."""
    try:
        page.click("button.js__accept-all-consents", timeout=3000)
        page.wait_for_timeout(500)
    except Exception:
        pass
