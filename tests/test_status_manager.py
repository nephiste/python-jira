import pytest
from unittest.mock import Mock
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from app.services.status_manager import StatusManager
from app.models import Task, TaskStatusHistory


@pytest.fixture
# Tworzy instancję StatusManager przed każdym testem
def status_manager():
    return StatusManager()


@pytest.fixture(autouse=True)
# Podmienia `db.session` w module, aby nie dotyczyć prawdziwej bazy
def patch_db(mocker):
    db_mock = mocker.patch("app.services.status_manager.db", autospec=True)
    db_mock.session = mocker.Mock()
    return db_mock


def test_change_status_success(mocker, status_manager, patch_db):
    """
    Testuje change_status: sukces zmiany statusu i zapis historii
    - Task istnieje
    - Tworzymy TaskStatusHistory
    - Oczekujemy dwa commity i jedno dodanie historii
    """
    # Przygotowanie mockowanego zadania z początkowym status
    mock_task = Mock(status="Open")
    query = Mock(get=Mock(return_value=mock_task))
    mocker.patch(
        "app.services.status_manager.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )

    # Przygotowanie historii statusu
    history = Mock()
    mocker.patch(
        "app.services.status_manager.TaskStatusHistory",
        return_value=history
    )

    # Wywołanie metody
    result = status_manager.change_status(
        task_id=1, new_status="Closed", changed_by_id=42
    )

    # Sprawdzenie:
    assert result is mock_task
    assert mock_task.status == "Closed"
    assert patch_db.session.commit.call_count == 2
    patch_db.session.add.assert_called_once_with(history)


def test_change_status_task_not_found(mocker, status_manager):
    """
    Testuje change_status: brak zadania -> ValueError
    """
    query = Mock(get=Mock(return_value=None))
    mocker.patch(
        "app.services.status_manager.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )

    with pytest.raises(ValueError, match="Zadanie o podanym ID nie istnieje"):
        status_manager.change_status(
            task_id=99, new_status="X", changed_by_id=1
        )


def test_change_status_rollback_on_update_error(mocker, status_manager, patch_db):
    """
    Testuje change_status: błąd pierwszego commit -> rollback
    """
    mock_task = Mock(status="A")
    query = Mock(get=Mock(return_value=mock_task))
    mocker.patch(
        "app.services.status_manager.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )
    history = Mock()
    mocker.patch(
        "app.services.status_manager.TaskStatusHistory",
        return_value=history
    )

    # Pierwszy commit rzuca Exception
    patch_db.session.commit.side_effect = Exception("update failed")

    with pytest.raises(Exception, match="update failed"):
        status_manager.change_status(
            task_id=1, new_status="B", changed_by_id=2
        )
    patch_db.session.rollback.assert_called_once()


def test_change_status_rollback_on_history_error(mocker, status_manager, patch_db):
    """
    Testuje change_status: pierwszy commit OK, drugi rzuca -> rollback
    """
    mock_task = Mock(status="X")
    query = Mock(get=Mock(return_value=mock_task))
    mocker.patch(
        "app.services.status_manager.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )
    history = Mock()
    mocker.patch(
        "app.services.status_manager.TaskStatusHistory",
        return_value=history
    )

    # Commitment: za pierwszym razem OK, za drugim wyjątek
    def commit_side_effect():
        if patch_db.session.commit.call_count == 1:
            return None
        raise Exception("history failed")
    patch_db.session.commit.side_effect = commit_side_effect

    with pytest.raises(Exception, match="history failed"):
        status_manager.change_status(
            task_id=2, new_status="Y", changed_by_id=3
        )
    patch_db.session.rollback.assert_called_once()


def test_get_history_for_task(mocker, status_manager):
    """
    Testuje get_history_for_task: pobiera historię posortowaną malejąco
    """
    fake = [Mock(), Mock()]
    query = Mock(
        filter_by=Mock(return_value=Mock(
            order_by=Mock(return_value=Mock(all=Mock(return_value=fake)))
        ))
    )
    mocker.patch(
        "app.services.status_manager.TaskStatusHistory.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )

    result = status_manager.get_history_for_task(task_id=5)
    assert result == fake
