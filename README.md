# Testy automatyczne - pantuniestal.com

Zautomatyzowane testy E2E sklepu internetowego [pantuniestal.com](https://pantuniestal.com) napisane w **Playwright** (Python).

## Wymagania

- Python 3.10+
- pip

## Instalacja

```bash
# 1. Sklonuj repozytorium
git clone <url-repo>
cd PlaywrightExample

# 2. Utwórz i aktywuj wirtualne środowisko
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 3. Zainstaluj zależności
pip install pytest-playwright

# 4. Zainstaluj przeglądarkę Chromium
playwright install chromium
```

## Uruchamianie testów

```bash
# Wszystkie testy
python3 -m pytest tests/ -v --browser chromium

# Pojedynczy plik
python3 -m pytest tests/test_cart.py -v --browser chromium

# Pojedynczy test
python3 -m pytest tests/test_cart.py::TestTC001AddProductFromCategory -v --browser chromium

# Z widoczna przegladarka (headed mode)
python3 -m pytest tests/ -v --browser chromium --headed
```

## Struktura projektu

```
PlaywrightExample/
├── conftest.py              # Konfiguracja Playwright (viewport, locale, timeout)
├── pytest.ini               # Konfiguracja pytest
├── README.md
├── TestCaseScenario/        # Dokumentacja test case'ow (.docx)
└── tests/
    ├── test_cart.py          # Testy koszyka (TC001-TC006, TC017, TC018, TC020)
    ├── test_sorting.py       # Testy sortowania produktow (TC007-TC010)
    ├── test_login.py         # Testy logowania i konta (TC011-TC016)
    └── test_product.py       # Test strony produktu (TC019)
```

## Lista testow (20)

### Koszyk (9 testow)

| ID | Nazwa | Opis |
|----|-------|------|
| TC001 | Dodanie produktu z listy kategorii | Dodaje produkt do koszyka i weryfikuje jego obecnosc |
| TC002 | Dodanie tego samego produktu kilka razy | Sprawdza czy ilosc sie zwieksza |
| TC003 | Dodanie dwoch roznych produktow | Weryfikuje 2 produkty w koszyku i sume cen |
| TC004 | Usuniecie produktu z koszyka | Usuwa produkt i sprawdza pusty koszyk |
| TC005 | Usuniecie jednego z kilku produktow | Sprawdza czy pozostale produkty zostaja |
| TC006 | Komunikat pustego koszyka | Weryfikuje komunikat "koszyk jest pusty" |
| TC017 | Aktualizacja ceny po usunieciu | Sprawdza przeliczenie sumy po usunieciu |
| TC018 | Aktualizacja licznika koszyka | Weryfikuje licznik w ikonie koszyka |
| TC020 | Dodanie z karty produktu | Dodaje produkt ze strony szczegolowej |

### Sortowanie (4 testy)

| ID | Nazwa | Opis |
|----|-------|------|
| TC007 | Sortowanie od najnizszej ceny | Sprawdza kolejnosc rosnaca cen |
| TC008 | Sortowanie od najwyzszej ceny | Sprawdza kolejnosc malejaca cen |
| TC009 | Sortowanie A-Z | Weryfikuje kolejnosc alfabetyczna |
| TC010 | Sortowanie Z-A | Weryfikuje odwrocona kolejnosc alfabetyczna |

### Logowanie i konto (6 testow)

| ID | Nazwa | Opis |
|----|-------|------|
| TC011 | Logowanie poprawnymi danymi | Loguje sie i sprawdza dostep do konta |
| TC012 | Logowanie blednym haslem | Weryfikuje komunikat o blednych danych |
| TC013 | Walidacja pustych pol | Sprawdza walidacje pustego formularza |
| TC014 | Odzyskiwanie hasla | Weryfikuje przejscie na strone resetu hasla |
| TC015 | Konto bez logowania | Sprawdza czy pojawia sie formularz logowania |
| TC016 | Ulubione bez logowania | Weryfikuje przekierowanie na logowanie |

### Strona produktu (1 test)

| ID | Nazwa | Opis |
|----|-------|------|
| TC019 | Otwarcie strony produktu | Sprawdza nazwe, zdjecie i cene produktu |

## Konfiguracja

### Dane logowania (TC011)

W pliku `tests/test_login.py` uzupelnij zmienne:

```python
TEST_EMAIL = "twoj@email.com"
TEST_PASSWORD = "TwojeHaslo"
```

### Ustawienia przegladarki

W `conftest.py` mozna zmienic:

- **viewport** - rozdzielczosc okna (domyslnie 1280x720)
- **locale** - jezyk przegladarki (domyslnie pl-PL)
- **timeout** - maksymalny czas oczekiwania na element (domyslnie 15s)

python3 -m pytest tests/ -v --browser chromium --headed 
