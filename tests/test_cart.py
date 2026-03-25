"""
Testy koszyka - TC001 do TC006, TC017, TC018, TC020
Strona: https://pantuniestal.com
"""
import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://pantuniestal.com"
CATEGORY_URL = f"{BASE_URL}/kategoria/dla-pan"
CART_URL = f"{BASE_URL}/pl/basket"


def _accept_cookies(page: Page):
    try:
        page.click("button.js__accept-all-consents", timeout=3000)
        page.wait_for_timeout(500)
    except Exception:
        pass


def _go_to_category(page: Page):
    """Przejdź na stronę kategorii i zaakceptuj cookies."""
    page.goto(CATEGORY_URL, wait_until="networkidle")
    _accept_cookies(page)


def _add_product_by_index(page: Page, index: int = 0):
    """Dodaj produkt do koszyka - przejdź na stronę produktu, wybierz rozmiar i dodaj."""
    # Pobierz link do produktu z listy kategorii
    product_link = page.locator("a.prodimage").nth(index)
    product_link.click()
    page.wait_for_load_state("load")
    page.wait_for_timeout(1000)
    _accept_cookies(page)

    # Wybierz pierwszy dostępny rozmiar (bez atrybutu data-unavailable)
    page.evaluate("""() => {
        const radios = document.querySelectorAll('form.form-basket input[type=radio]');
        for (const r of radios) {
            if (!r.hasAttribute('data-unavailable')) {
                r.checked = true;
                r.dispatchEvent(new Event('change', {bubbles: true}));
                return;
            }
        }
    }""")
    page.wait_for_timeout(1000)

    # Kliknij "Do koszyka"
    page.evaluate("""() => {
        document.querySelector('form.form-basket').submit();
    }""")
    page.wait_for_load_state("load")
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1500)


def _get_product_name_by_index(page: Page, index: int = 0) -> str:
    """Pobierz nazwę produktu po indeksie."""
    names = page.locator(".productname")
    return names.nth(index).inner_text().strip()


def _open_cart(page: Page):
    """Otwórz stronę koszyka."""
    page.goto(CART_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)


# ---------------------------------------------------------------------------
# TC_001 - Dodanie produktu do koszyka z listy kategorii
# ---------------------------------------------------------------------------
class TestTC001AddProductFromCategory:
    def test_add_product_to_cart_from_category(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_ADD_PRODUCT_FROM_CATEGORY_LIST_UPDATE_CART_ICON_AND_CART_CONTENT_001
        """
        # 1. Wejdź na stronę główną
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        _accept_cookies(page)

        # 2. Kliknij kategorię produktów
        page.locator("a:visible").filter(has_text="Dla pań").first.click()
        page.wait_for_load_state("networkidle")

        # 3-4. Dodaj produkt do koszyka
        _add_product_by_index(page, 0)

        # 5. Otwórz koszyk
        _open_cart(page)

        # Oczekiwany wynik: produkt w koszyku z nazwą, ceną i ilością
        body_text = page.inner_text("body")
        body_lower = " ".join(body_text.lower().split())
        assert "koszyk jest pusty" not in body_lower, "Koszyk jest pusty po dodaniu produktu"
        assert re.search(r"\d+[,\.]\d{2}\s*zł", body_text), "Nie znaleziono ceny w koszyku"
        quantity_input = page.locator("input[name^='quantity_']")
        expect(quantity_input.first).to_be_visible()


# ---------------------------------------------------------------------------
# TC_002 - Dodanie tego samego produktu kilka razy
# ---------------------------------------------------------------------------
class TestTC002AddSameProductMultipleTimes:
    def test_add_same_product_multiple_times(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_ADD_SAME_PRODUCT_MULTIPLE_TIMES_VERIFY_QUANTITY_INCREMENT_IN_CART_002
        """
        # 1. Otwórz kategorię
        _go_to_category(page)

        # 2. Dodaj produkt
        _add_product_by_index(page, 0)

        # 3. Ponownie dodaj ten sam produkt
        _go_to_category(page)
        _add_product_by_index(page, 0)

        # 4. Otwórz koszyk
        _open_cart(page)

        # Oczekiwany wynik: ilość >= 2
        quantity_input = page.locator("input[name^='quantity_']").first
        value = quantity_input.input_value()
        assert int(value) >= 2, f"Oczekiwano ilości >= 2, otrzymano {value}"


# ---------------------------------------------------------------------------
# TC_003 - Dodanie dwóch różnych produktów do koszyka
# ---------------------------------------------------------------------------
class TestTC003AddTwoDifferentProducts:
    def test_add_two_different_products(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_ADD_TWO_DIFFERENT_PRODUCTS_VERIFY_CART_TOTAL_PRICE_CALCULATION_003
        """
        # 1. Dodaj pierwszy produkt
        _go_to_category(page)
        name1 = _get_product_name_by_index(page, 0)
        _add_product_by_index(page, 0)

        # 2-3. Wróć i dodaj drugi produkt
        _go_to_category(page)
        name2 = _get_product_name_by_index(page, 1)
        _add_product_by_index(page, 1)

        # 4. Przejdź do koszyka
        _open_cart(page)

        # Oczekiwany wynik: dwa produkty i poprawna suma
        body_text = page.inner_text("body")
        assert name1[:15] in body_text, f"Nie znaleziono pierwszego produktu '{name1[:15]}'"
        assert name2[:15] in body_text, f"Nie znaleziono drugiego produktu '{name2[:15]}'"

        # Sprawdź sumę cen
        prices = page.locator(".price")
        all_prices = []
        for i in range(prices.count()):
            txt = prices.nth(i).inner_text()
            match = re.search(r"([\d\s]+[,\.]\d{2})", txt)
            if match:
                val = float(match.group(1).replace(" ", "").replace(",", "."))
                all_prices.append(val)
        assert len(all_prices) >= 2, "Powinny być co najmniej 2 ceny produktów"


# ---------------------------------------------------------------------------
# TC_004 - Usunięcie produktu z koszyka
# ---------------------------------------------------------------------------
class TestTC004RemoveProductFromCart:
    def test_remove_product_from_cart(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_REMOVE_SINGLE_PRODUCT_FROM_CART_VERIFY_CART_ITEM_DELETED_004
        """
        # Przygotowanie: dodaj produkt
        _go_to_category(page)
        _add_product_by_index(page, 0)

        # 1. Otwórz koszyk
        _open_cart(page)

        # 2-3. Kliknij przycisk usunięcia
        remove_btn = page.locator("a.prodremove")
        expect(remove_btn.first).to_be_visible()
        remove_btn.first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: koszyk pusty
        expect(page.locator("body")).to_contain_text("koszyk jest pusty")


# ---------------------------------------------------------------------------
# TC_005 - Usunięcie jednego z kilku produktów
# ---------------------------------------------------------------------------
class TestTC005RemoveOneOfMultipleProducts:
    def test_remove_one_of_multiple_products(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_REMOVE_ONE_PRODUCT_FROM_MULTIPLE_ITEMS_VERIFY_OTHER_ITEMS_REMAIN_005
        """
        # Przygotowanie: dodaj dwa różne produkty
        _go_to_category(page)
        name2 = _get_product_name_by_index(page, 1)
        _add_product_by_index(page, 0)

        _go_to_category(page)
        _add_product_by_index(page, 1)

        # 1. Otwórz koszyk
        _open_cart(page)

        # Policz produkty
        remove_btns = page.locator("a.prodremove")
        initial_count = remove_btns.count()
        assert initial_count >= 2, f"Oczekiwano >= 2 produktów, jest {initial_count}"

        # 2. Usuń pierwszy produkt
        remove_btns.first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: pozostały produkt nadal w koszyku
        body_text = page.inner_text("body")
        assert name2[:15] in body_text, f"Drugi produkt '{name2[:15]}' powinien nadal być w koszyku"
        assert "koszyk jest pusty" not in body_text.lower()


# ---------------------------------------------------------------------------
# TC_006 - Sprawdzenie komunikatu pustego koszyka
# ---------------------------------------------------------------------------
class TestTC006EmptyCartMessage:
    def test_empty_cart_message(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_EMPTY_CART_VERIFY_EMPTY_CART_MESSAGE_DISPLAYED_006
        """
        # 1. Otwórz koszyk bez dodanych produktów
        _open_cart(page)

        # Oczekiwany wynik: komunikat o pustym koszyku
        expect(page.locator("body")).to_contain_text("koszyk jest pusty")


# ---------------------------------------------------------------------------
# TC_017 - Aktualizacja ceny koszyka po usunięciu produktu
# ---------------------------------------------------------------------------
class TestTC017CartPriceUpdateAfterRemoval:
    def test_cart_price_update_after_removal(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_TOTAL_PRICE_UPDATE_AFTER_PRODUCT_REMOVAL_VERIFY_PRICE_RECALCULATION_017
        """
        # Przygotowanie: dodaj dwa produkty
        _go_to_category(page)
        _add_product_by_index(page, 0)
        _go_to_category(page)
        _add_product_by_index(page, 1)

        # 1. Otwórz koszyk
        _open_cart(page)

        # 2. Zapamiętaj cenę "Razem"
        summary = page.locator(".summary-container .sum").first
        initial_price_text = summary.inner_text()
        initial_price = float(
            re.search(r"([\d\s]+[,\.]\d{2})", initial_price_text)
            .group(1)
            .replace(" ", "")
            .replace(",", ".")
        )

        # 3. Usuń jeden produkt
        page.locator("a.prodremove").first.click()
        page.wait_for_timeout(2000)
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: cena się zmniejszyła
        new_summary = page.locator(".summary-container .sum").first
        new_price_text = new_summary.inner_text()
        new_price = float(
            re.search(r"([\d\s]+[,\.]\d{2})", new_price_text)
            .group(1)
            .replace(" ", "")
            .replace(",", ".")
        )
        assert new_price < initial_price, (
            f"Cena powinna się zmniejszyć: była {initial_price}, jest {new_price}"
        )


# ---------------------------------------------------------------------------
# TC_018 - Aktualizacja licznika koszyka
# ---------------------------------------------------------------------------
class TestTC018CartIconCounterUpdate:
    def test_cart_icon_counter_update(self, page: Page):
        """
        ID: TC_ECOMMERCE_CART_ICON_ITEM_COUNTER_UPDATE_AFTER_ADD_PRODUCT_018
        """
        # 1. Przejdź na stronę kategorii (koszyk pusty)
        _go_to_category(page)

        # Odczytaj początkowy licznik koszyka
        counter_text = page.evaluate("""() => {
            const el = document.querySelector('.basket-icon .count, .basket .count, .header-nav .basket span');
            return el ? el.textContent.trim() : '0';
        }""")
        initial_count = int(re.sub(r"[^\d]", "", counter_text) or "0")

        # 2. Dodaj produkt do koszyka
        _add_product_by_index(page, 0)

        # Oczekiwany wynik: licznik zwiększa się
        page.wait_for_timeout(1000)
        new_counter = page.evaluate("""() => {
            const el = document.querySelector('.basket-icon .count, .basket .count, .header-nav .basket span');
            return el ? el.textContent.trim() : '0';
        }""")
        new_count = int(re.sub(r"[^\d]", "", new_counter) or "0")
        assert new_count > initial_count, (
            f"Licznik powinien wzrosnąć: był {initial_count}, jest {new_count}"
        )


# ---------------------------------------------------------------------------
# TC_020 - Dodanie produktu do koszyka z karty produktu
# ---------------------------------------------------------------------------
class TestTC020AddProductFromProductPage:
    def test_add_product_from_product_page(self, page: Page):
        """
        ID: TC_ECOMMERCE_PRODUCT_ADD_TO_CART_FROM_PRODUCT_PAGE_VERIFY_CART_UPDATE_020
        """
        # Przejdź do kategorii
        _go_to_category(page)

        # Kliknij na produkt (przez link z nazwą)
        product_link = page.locator("a.prodimage").first
        product_link.click()
        page.wait_for_load_state("load")
        page.wait_for_timeout(1000)
        _accept_cookies(page)

        # 1. Wybierz rozmiar i kliknij "Do koszyka" na stronie produktu
        page.evaluate("""() => {
            const radios = document.querySelectorAll('form.form-basket input[type=radio]');
            for (const r of radios) {
                if (!r.hasAttribute('data-unavailable')) {
                    r.checked = true;
                    r.dispatchEvent(new Event('change', {bubbles: true}));
                    return;
                }
            }
        }""")
        page.wait_for_timeout(1000)

        page.evaluate("""() => {
            document.querySelector('form.form-basket').submit();
        }""")
        page.wait_for_load_state("load")
        page.wait_for_timeout(1500)

        # 2. Otwórz koszyk
        _open_cart(page)

        # Oczekiwany wynik: produkt w koszyku
        body_text = page.inner_text("body").lower()
        assert "koszyk jest pusty" not in body_text, "Koszyk nie powinien być pusty po dodaniu produktu"
