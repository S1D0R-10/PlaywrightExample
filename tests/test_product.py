"""
Test strony produktu - TC019
Strona: https://pantuniestal.com
"""
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


# ---------------------------------------------------------------------------
# TC_019 - Otwarcie strony produktu
# ---------------------------------------------------------------------------
class TestTC019ProductPageDetails:
    def test_product_page_displays_details(self, page: Page):
        """
        ID: TC_ECOMMERCE_PRODUCT_PAGE_OPEN_VERIFY_PRODUCT_DETAILS_DISPLAYED_CORRECTLY_019
        """
        # Przejdź do kategorii
        page.goto(CATEGORY_URL)
        page.wait_for_load_state("networkidle")
        _accept_cookies(page)

        # 1. Kliknij nazwę produktu
        page.locator("a.prodimage").first.click()
        page.wait_for_load_state("networkidle")

        # Oczekiwany wynik: strona z nazwą, zdjęciem i ceną

        # Nazwa produktu (h1.name)
        heading = page.locator("h1.name, h1")
        expect(heading.first).to_be_visible()
        name_text = heading.first.inner_text()
        assert len(name_text) > 0, "Nazwa produktu nie powinna być pusta"

        # Zdjęcie produktu
        product_image = page.locator("img[data-src*='productGfx'], img[src*='productGfx']").first
        expect(product_image).to_be_attached()

        # Cena produktu
        price_el = page.locator(".price em, .price")
        expect(price_el.first).to_be_visible()
        price_text = price_el.first.inner_text()
        assert re.search(r"\d+[,\.]\d{2}\s*zł", price_text), f"Nie znaleziono ceny: '{price_text}'"
