"""
Testy logowania i konta - TC011 do TC016
Strona: https://pantuniestal.com
"""
import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://pantuniestal.com"
LOGIN_URL = f"{BASE_URL}/pl/login"

# Dane testowe - uzupełnij prawdziwe dane aby odblokować TC011
TEST_EMAIL = "szymonnnek.pl@gmail.com"
TEST_PASSWORD = "TestPassword123!"


def _accept_cookies(page: Page):
    try:
        page.click("button.js__accept-all-consents", timeout=3000)
        page.wait_for_timeout(500)
    except Exception:
        pass


def _go_to_login(page: Page):
    page.goto(LOGIN_URL)
    page.wait_for_load_state("networkidle")
    _accept_cookies(page)


# ---------------------------------------------------------------------------
# TC_011 - Logowanie poprawnymi danymi
# ---------------------------------------------------------------------------
class TestTC011LoginWithValidCredentials:
    def test_login_with_valid_credentials(self, page: Page):
        """
        ID: TC_ECOMMERCE_LOGIN_WITH_VALID_CREDENTIALS_VERIFY_SUCCESSFUL_ACCOUNT_LOGIN_011
        """
        # 1. Kliknij przycisk "Konto" -> przejście na stronę logowania
        _go_to_login(page)

        # 2. Wpisz poprawny e-mail
        page.fill("#mail_input_long", TEST_EMAIL)

        # 3. Wpisz poprawne hasło
        page.fill("#pass_input_long", TEST_PASSWORD)

        # 4. Kliknij "Zaloguj się"
        page.locator("button.login:visible").click()
        page.wait_for_timeout(3000)
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: użytkownik zalogowany, ma dostęp do panelu konta
        expect(page).not_to_have_url(re.compile(r"/pl/login$"))
        body_text = page.inner_text("body")
        assert "Niepoprawne dane logowania" not in body_text, "Logowanie nie powiodło się"


# ---------------------------------------------------------------------------
# TC_012 - Logowanie błędnym hasłem
# ---------------------------------------------------------------------------
class TestTC012LoginWithInvalidPassword:
    def test_login_with_invalid_password(self, page: Page):
        """
        ID: TC_ECOMMERCE_LOGIN_WITH_INVALID_PASSWORD_VERIFY_ERROR_MESSAGE_DISPLAYED_012
        """
        _go_to_login(page)

        # 2. Wpisz e-mail
        page.fill("#mail_input_long", "testowy@email.com")

        # 3. Wpisz niepoprawne hasło
        page.fill("#pass_input_long", "BledneHaslo123!")

        # 4. Kliknij "Zaloguj się"
        page.locator("button.login:visible").click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: komunikat o błędnych danych
        expect(page.locator(".alert")).to_contain_text("Niepoprawne dane logowania")


# ---------------------------------------------------------------------------
# TC_013 - Walidacja pustych pól logowania
# ---------------------------------------------------------------------------
class TestTC013EmptyFieldsValidation:
    def test_empty_fields_validation(self, page: Page):
        """
        ID: TC_ECOMMERCE_LOGIN_EMPTY_FIELDS_VALIDATION_VERIFY_LOGIN_FORM_VALIDATION_MESSAGES_013
        """
        _go_to_login(page)

        # 1. Nie wpisuj żadnych danych
        # 2. Kliknij "Zaloguj się"
        page.locator("button.login:visible").click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: system wyświetla komunikat o wymaganych polach / błędnych danych
        expect(page.locator(".alert")).to_contain_text("Niepoprawne dane logowania")


# ---------------------------------------------------------------------------
# TC_014 - Przejście do odzyskiwania hasła
# ---------------------------------------------------------------------------
class TestTC014PasswordResetLinkNavigation:
    def test_password_reset_link_navigation(self, page: Page):
        """
        ID: TC_ECOMMERCE_PASSWORD_RESET_LINK_NAVIGATION_VERIFY_PASSWORD_RESET_PAGE_LOAD_014
        """
        _go_to_login(page)

        # 1. Kliknij "Nie pamiętasz hasła?"
        page.locator("a[href='/pl/passremind']:visible").click()
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: strona resetowania hasła
        expect(page).to_have_url(re.compile(r"passremind"))


# ---------------------------------------------------------------------------
# TC_015 - Próba wejścia do konta bez logowania
# ---------------------------------------------------------------------------
class TestTC015AccountAccessWithoutLogin:
    def test_account_access_without_login(self, page: Page):
        """
        ID: TC_ECOMMERCE_ACCOUNT_ACCESS_WITHOUT_LOGIN_VERIFY_REDIRECT_TO_LOGIN_PAGE_015
        """
        # 1. Kliknij ikonę "Konto" na stronie głównej
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        _accept_cookies(page)

        page.locator(".acount-icon, .account-icon").first.click()
        page.wait_for_timeout(2000)

        # Oczekiwany wynik: system wyświetla formularz logowania (sidebar/overlay)
        login_form = page.locator("input[name='mail']:visible")
        expect(login_form.first).to_be_visible()
        login_btn = page.locator("button.login:visible")
        expect(login_btn.first).to_be_visible()


# ---------------------------------------------------------------------------
# TC_016 - Wejście w ulubione bez logowania
# ---------------------------------------------------------------------------
class TestTC016FavouritesAccessWithoutLogin:
    def test_favourites_access_without_login(self, page: Page):
        """
        ID: TC_ECOMMERCE_ACCOUNT_FAVOURITES_ACCESS_WITHOUT_LOGIN_VERIFY_LOGIN_REQUIRED_016
        """
        # 1. Kliknij sekcję "Ulubione"
        page.goto(f"{BASE_URL}/pl/panel/favourites")
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: przekierowanie na stronę logowania
        expect(page).to_have_url(re.compile(r"login"))
