import pytest
from datetime import timedelta
import app.services.deadline_validator as dv_mod
from app.services.deadline_validator import DeadlineValidator


@pytest.fixture(autouse=True)
# Zamraża "teraz" wewnątrz modułu, aby testy były deterministyczne
# FixedDatetime.utcnow() zawsze zwraca 2025-06-29T12:00:00

def fixed_datetime(monkeypatch):
    class FixedDatetime(dv_mod.datetime):
        @classmethod
        def utcnow(cls):
            return cls(2025, 6, 29, 12, 0, 0)
    monkeypatch.setattr(dv_mod, "datetime", FixedDatetime)
    return FixedDatetime.utcnow()


@pytest.fixture
# Tworzy instancję validatora przed każdym testem

def validator():
    return DeadlineValidator()


def test_is_valid_deadline_none(validator):
    """
    Testuje is_valid_deadline: wejściowe None
    Oczekuje False (brak deadline)
    """
    assert validator.is_valid_deadline(None) is False


def test_is_valid_deadline_wrong_type(validator):
    """
    Testuje is_valid_deadline: nie-datetime
    Oczekuje ValueError o typie argumentu
    """
    with pytest.raises(ValueError, match="Deadline musi być obiektem datetime"):
        validator.is_valid_deadline("2025-06-30")


def test_is_valid_deadline_past(validator, fixed_datetime):
    """
    Testuje is_valid_deadline: data przeszła (< teraz)
    Oczekuje False
    """
    past = dv_mod.datetime(2020, 1, 1, 0, 0, 0)
    assert validator.is_valid_deadline(past) is False


def test_is_valid_deadline_now(validator, fixed_datetime):
    """
    Testuje is_valid_deadline: dokładnie teraz
    Oczekuje True
    """
    now = dv_mod.datetime.utcnow()
    assert validator.is_valid_deadline(now) is True


def test_is_valid_deadline_future(validator, fixed_datetime):
    """
    Testuje is_valid_deadline: przyszła data (> teraz)
    Oczekuje True
    """
    future = dv_mod.datetime.utcnow() + timedelta(days=1)
    assert validator.is_valid_deadline(future) is True
