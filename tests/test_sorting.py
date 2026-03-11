"""
Testy sortowania produktów - TC007 do TC010
Strona: https://pantuniestal.com
"""
import locale
import re

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://pantuniestal.com"
CATEGORY_URL = f"{BASE_URL}/kategoria/dla-pan"


def _accept_cookies(page: Page):
    try:
        page.click("button.js__accept-all-consents", timeout=3000)
        page.wait_for_timeout(500)
    except Exception:
        pass


def _go_to_category(page: Page):
    page.goto(CATEGORY_URL)
    page.wait_for_load_state("networkidle")
    _accept_cookies(page)


def _select_sorting(page: Page, label: str):
    """Wybierz opcję sortowania z select.gotourl (nawiguje do nowego URL)."""
    page.locator("select.gotourl").select_option(label=label)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(1000)


def _get_product_prices(page: Page) -> list[float]:
    """Pobierz ceny produktów widocznych na stronie (pierwsze 10)."""
    prices = []
    price_elements = page.locator(".product-inner-wrap .price em, .product-inner-wrap .price")
    count = min(price_elements.count(), 10)
    for i in range(count):
        text = price_elements.nth(i).inner_text()
        match = re.search(r"([\d\s]+[,\.]\d{2})", text)
        if match:
            val = float(match.group(1).replace(" ", "").replace(",", "."))
            prices.append(val)
    return prices


def _get_product_names(page: Page) -> list[str]:
    """Pobierz nazwy produktów widocznych na stronie (pierwsze 10)."""
    names = []
    name_elements = page.locator(".productname")
    count = min(name_elements.count(), 10)
    for i in range(count):
        names.append(name_elements.nth(i).inner_text().strip())
    return names


# ---------------------------------------------------------------------------
# TC_007 - Sortowanie od najniższej ceny
# ---------------------------------------------------------------------------
class TestTC007SortByPriceAscending:
    def test_sort_by_price_ascending(self, page: Page):
        """
        ID: TC_ECOMMERCE_PRODUCT_SORT_BY_PRICE_ASCENDING_VERIFY_LOWEST_PRICE_FIRST_007
        """
        _go_to_category(page)
        _select_sorting(page, "Od najniższej ceny")

        prices = _get_product_prices(page)
        assert len(prices) >= 2, f"Za mało cen: {prices}"
        for i in range(len(prices) - 1):
            assert prices[i] <= prices[i + 1], (
                f"Ceny nie rosnące: {prices[i]} > {prices[i + 1]} (poz. {i}, {i + 1})"
            )


# ---------------------------------------------------------------------------
# TC_008 - Sortowanie od najwyższej ceny
# ---------------------------------------------------------------------------
class TestTC008SortByPriceDescending:
    def test_sort_by_price_descending(self, page: Page):
        """
        ID: TC_ECOMMERCE_PRODUCT_SORT_BY_PRICE_DESCENDING_VERIFY_HIGHEST_PRICE_FIRST_008
        """
        _go_to_category(page)
        _select_sorting(page, "Od najwyższej ceny")

        prices = _get_product_prices(page)
        assert len(prices) >= 2, f"Za mało cen: {prices}"
        for i in range(len(prices) - 1):
            assert prices[i] >= prices[i + 1], (
                f"Ceny nie malejące: {prices[i]} < {prices[i + 1]} (poz. {i}, {i + 1})"
            )


# ---------------------------------------------------------------------------
# TC_009 - Sortowanie alfabetycznie A-Z
# ---------------------------------------------------------------------------
class TestTC009SortByNameAZ:
    def test_sort_by_name_ascending(self, page: Page):
        """
        ID: TC_ECOMMERCE_PRODUCT_SORT_BY_NAME_ASCENDING_VERIFY_ALPHABETICAL_ORDER_A_TO_Z_009
        """
        _go_to_category(page)
        _select_sorting(page, "Nazwa produktu od A do Z")

        names = _get_product_names(page)
        assert len(names) >= 2, f"Za mało nazw: {names}"

        try:
            locale.setlocale(locale.LC_COLLATE, "pl_PL.UTF-8")
        except locale.Error:
            locale.setlocale(locale.LC_COLLATE, "")
        sorted_names = sorted(names, key=locale.strxfrm)
        assert names == sorted_names, (
            f"Nazwy nie posortowane A-Z.\nOtrzymano: {names}\nOczekiwano: {sorted_names}"
        )


# ---------------------------------------------------------------------------
# TC_010 - Sortowanie alfabetycznie Z-A
# ---------------------------------------------------------------------------
class TestTC010SortByNameZA:
    def test_sort_by_name_descending(self, page: Page):
        """
        ID: TC_ECOMMERCE_PRODUCT_SORT_BY_NAME_DESCENDING_VERIFY_ALPHABETICAL_ORDER_Z_TO_A_010
        """
        _go_to_category(page)
        _select_sorting(page, "Nazwa produktu od Z do A")

        names = _get_product_names(page)
        assert len(names) >= 2, f"Za mało nazw: {names}"

        # Serwer sortuje z uwzgl. polskiej lokalizacji - sprawdź z locale.strxfrm
        try:
            locale.setlocale(locale.LC_COLLATE, "pl_PL.UTF-8")
        except locale.Error:
            locale.setlocale(locale.LC_COLLATE, "")
        sorted_names = sorted(names, key=locale.strxfrm, reverse=True)
        assert names == sorted_names, (
            f"Nazwy nie posortowane Z-A.\nOtrzymano: {names}\nOczekiwano: {sorted_names}"
        )
