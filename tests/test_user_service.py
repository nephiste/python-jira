import pytest
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from unittest.mock import Mock

from app.services.user_service import UserService
from app.models import User


@pytest.fixture
# Tworzy instancję UserService przed każdym testem

def user_service():
    return UserService()


@pytest.fixture
# Podmienia `db` w module serwisu, by izolować logikę od prawdziwej bazy

def mock_db(mocker):
    return mocker.patch("app.services.user_service.db")


def test_register_user_success(mocker, user_service, mock_db):
    """
    Testuje register_user: brak duplikatu, poprawne dane
    Oczekuje nowego użytkownika, add + commit
    """
    # brak istniejącego usera
    mocker.patch(
        "app.services.user_service.User.query.filter",
        return_value=Mock(first=lambda: None)
    )
    # proste ustawienie hasła na "hashed_" + p
    mocker.patch(
        "app.models.User.set_password",
        lambda self, p: setattr(self, "password_hash", "hashed_" + p)
    )

    user = user_service.register_user("testuser", "test@example.com", "password123")

    assert user.username == "testuser"
    assert user.password_hash == "hashed_password123"
    mock_db.session.add.assert_called_once_with(user)
    mock_db.session.commit.assert_called_once()


def test_register_user_missing_fields(user_service):
    """
    Testuje register_user: brak któregokolwiek pola -> ValueError
    """
    with pytest.raises(ValueError, match="Wszystkie pola są wymagane"):
        user_service.register_user("", "a@b.com", "p")
    with pytest.raises(ValueError, match="Wszystkie pola są wymagane"):
        user_service.register_user("u", "", "p")
    with pytest.raises(ValueError, match="Wszystkie pola są wymagane"):
        user_service.register_user("u", "a@b.com", "")


def test_register_user_duplicate(mocker, user_service):
    """
    Testuje register_user: istnieje już user o tej samej nazwie lub emailu -> ValueError
    """
    mocker.patch(
        "app.services.user_service.User.query.filter",
        return_value=Mock(first=lambda: object())
    )
    with pytest.raises(ValueError, match="Użytkownik o podanej nazwie lub emailu już istnieje"):
        user_service.register_user("existing", "x@y.com", "pwd")


def test_register_user_db_error(mocker, user_service):
    """
    Testuje register_user: commit rzuca IntegrityError -> rollback + ValueError
    """
    # brak duplikatu
    filter_mock = mocker.Mock()
    filter_mock.first.return_value = None
    mocker.patch(
        "app.services.user_service.User.query.filter",
        return_value=filter_mock
    )
    # commit rzuca IntegrityError
    db_mock = mocker.patch("app.services.user_service.db")
    db_mock.session.commit.side_effect = IntegrityError("s", "p", "o")

    with pytest.raises(ValueError, match="Błąd przy zapisie użytkownika do bazy"):
        user_service.register_user("test12", "test@example.com", "password123")
    db_mock.session.rollback.assert_called_once()


def test_authenticate_user_success(mocker, user_service):
    """
    Testuje authenticate_user: poprawne hasło -> zwraca user
    """
    mock_user = mocker.Mock()
    mock_user.check_password.return_value = True

    query_mock = mocker.Mock()
    query_mock.filter_by.return_value = query_mock
    query_mock.first.return_value = mock_user
    mocker.patch(
        "app.services.user_service.User.query",
        new_callable=mocker.PropertyMock,
        return_value=query_mock
    )

    result = user_service.authenticate_user("user", "pass")
    assert result is mock_user
    mock_user.check_password.assert_called_once_with("pass")


def test_authenticate_user_wrong_password(mocker, user_service):
    """
    Testuje authenticate_user: błędne hasło -> None
    """
    mock_user = Mock(check_password=Mock(return_value=False))
    mocker.patch(
        "app.services.user_service.User.query.filter_by",
        return_value=Mock(first=lambda: mock_user)
    )
    assert user_service.authenticate_user("user", "bad") is None


def test_authenticate_user_not_found(mocker, user_service):
    """
    Testuje authenticate_user: brak usera -> None
    """
    mocker.patch(
        "app.services.user_service.User.query.filter_by",
        return_value=Mock(first=lambda: None)
    )
    assert user_service.authenticate_user("no", "pass") is None


def test_get_user_by_id_found(mocker, user_service):
    """
    Testuje get_user_by_id: istniejący ID -> zwraca user
    """
    mock_user = Mock()
    query_mock = Mock(get=Mock(return_value=mock_user))
    mocker.patch(
        "app.services.user_service.User.query",
        new_callable=mocker.PropertyMock,
        return_value=query_mock
    )
    assert user_service.get_user_by_id(123) is mock_user


def test_get_user_by_id_not_found(mocker, user_service):
    """
    Testuje get_user_by_id: brak usera -> None
    """
    query_mock = Mock(get=Mock(return_value=None))
    mocker.patch(
        "app.services.user_service.User.query",
        new_callable=mocker.PropertyMock,
        return_value=query_mock
    )
    assert user_service.get_user_by_id(999) is None


def test_get_all_users(mocker, user_service):
    """
    Testuje get_all_users: zwraca listę userów
    """
    fake_list = [Mock(), Mock()]
    query_mock = Mock(all=Mock(return_value=fake_list))
    mocker.patch(
        "app.services.user_service.User.query",
        new_callable=mocker.PropertyMock,
        return_value=query_mock
    )
    assert user_service.get_all_users() == fake_list


def test_delete_user_success(mocker, user_service, mock_db):
    """
    Testuje delete_user: istniejący user -> usuwa i zwraca True
    """
    mock_user = Mock()
    mocker.patch.object(user_service, 'get_user_by_id', return_value=mock_user)
    assert user_service.delete_user(1) is True
    mock_db.session.delete.assert_called_once_with(mock_user)
    mock_db.session.commit.assert_called_once()


def test_delete_user_not_found(mocker, user_service):
    """
    Testuje delete_user: brak usera -> False
    """
    mocker.patch.object(user_service, 'get_user_by_id', return_value=None)
    assert user_service.delete_user(999) is False


def test_user_password_methods():
    """
    Testuje metody modelu User:
    - set_password generuje password_hash
    - check_password poprawnie weryfikuje hasło
    """
    u = User(username="x", email="y@test.pl", password_hash="")
    u.set_password("secret")
    assert u.password_hash != ""
    assert u.check_password("secret") is True
    assert u.check_password("wrong") is False
