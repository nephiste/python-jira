import pytest
from app.services.priority_handler import PriorityHandler


@pytest.fixture
# Tworzy instancję PriorityHandler przed każdym testem

def ph():
    return PriorityHandler()


@pytest.mark.parametrize("input_str,expected", [
    # normalize_priority: różne warianty tekstu prowadzą do jednego formatu
    ("wysoki", "High"),
    ("  High  ", "High"),
    ("WYSOKI", "High"),
    ("średni", "Medium"),
    ("Sredni", "Medium"),
    (" medium ", "Medium"),
    ("niski", "Low"),
    ("Low", "Low"),
    ("  LOW  ", "Low"),
    ("unknown", "Medium"),  # domyślnie Medium, gdy nieznany tekst
    ("", "Medium"),        # puste -> domyślny medium
])

def test_normalize_priority(ph, input_str, expected):
    """
    Testuje normalize_priority:
    - usuwa spacje
    - ignoruje wielkość liter
    - mapuje na High/Medium/Low, domyślnie Medium
    """
    assert ph.normalize_priority(input_str) == expected


@pytest.mark.parametrize("priority,valid", [
    # is_valid_priority: tylko predefiniowane wartości są dozwolone
    ("Low", True),
    ("Medium", True),
    ("High", True),
    ("low", False),       # wielkość liter ma znaczenie
    ("UNKNOWN", False),
    ("", False),
    (None, False),
])

def test_is_valid_priority(ph, priority, valid):
    """
    Testuje is_valid_priority:
    - powinno zwrócić True dla Low/Medium/High
    - False w przeciwnym wypadku
    """
    assert ph.is_valid_priority(priority) is valid


@pytest.mark.parametrize("p1,p2,expected", [
    # compare_priority: porównuje priorytety zgodnie z ustalonym order
    ("Low", "Low", 0),
    ("Low", "Medium", -1),
    ("Low", "High", -1),
    ("Medium", "Low", 1),
    ("Medium", "Medium", 0),
    ("Medium", "High", -1),
    ("High", "Low", 1),
    ("High", "Medium", 1),
    ("High", "High", 0),
])

def test_compare_priority(ph, p1, p2, expected):
    """
    Testuje compare_priority:
    - zwraca -1 gdy p1 < p2,
    - 0 gdy równe,
    - 1 gdy p1 > p2
    """
    assert ph.compare_priority(p1, p2) == expected
