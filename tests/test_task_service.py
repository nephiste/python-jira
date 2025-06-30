import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from unittest.mock import Mock

from app.services.task_service import TaskService
from app.models import Task


@pytest.fixture(autouse=True)
# Podmienia db.session oraz DeadlineValidator w module TaskService
# Umożliwia testowanie logiki bez rzeczywistej bazy i daty

def patch_db_and_validator(mocker):
    db_mock = mocker.patch("app.services.task_service.db", autospec=True)
    db_mock.session = mocker.Mock()
    val_cls = mocker.patch("app.services.task_service.DeadlineValidator", autospec=True)
    val_inst = val_cls.return_value
    # Domyślnie wszystkie deadliny są uznawane za poprawne
    val_inst.is_valid_deadline.return_value = True
    return {"db": db_mock, "validator": val_inst}


@pytest.fixture
# Tworzy instancję serwisu zadań przed każdym testem

def task_service():
    return TaskService()


def test_create_task_success(patch_db_and_validator, task_service):
    """
    Testuje create_task: poprawne dane + deadline w przyszłości
    Oczekuje utworzenie Task, dodanie do sesji i commit
    """
    task = task_service.create_task(
        project_id=1,
        title="Nowe zadanie",
        description="Opis testowy",
        created_by_id=10,
        assigned_to_id=20,
        deadline="2035-12-31",
        priority="High"
    )
    assert isinstance(task, Task)
    assert task.title == "Nowe zadanie"
    assert task.priority == "High"
    patch_db_and_validator["db"].session.add.assert_called_once_with(task)
    patch_db_and_validator["db"].session.commit.assert_called_once()


def test_create_task_without_required_fields(task_service):
    """
    Testuje create_task: brak wymaganych pól project_id/title/created_by_id
    Oczekuje ValueError o brakujących polach
    """
    with pytest.raises(ValueError, match="Brak wymaganych pól"):
        task_service.create_task(
            project_id=None,
            title=None,
            description="",
            created_by_id=None,
            assigned_to_id=None,
            deadline=None,
            priority=None
        )


def test_create_task_invalid_deadline_format(task_service):
    """
    Testuje create_task: niepoprawny format daty string
    Oczekuje ValueError o formacie daty
    """
    with pytest.raises(ValueError, match="Niepoprawny format daty"):
        task_service.create_task(
            project_id=1,
            title="Złe daty",
            description="x",
            created_by_id=1,
            assigned_to_id=1,
            deadline="invalid-date",
            priority="Low"
        )


def test_create_task_past_deadline(patch_db_and_validator, task_service):
    """
    Testuje create_task: deadline uznany za przeszły przez validator
    Oczekuje ValueError o przyszłości daty
    """
    # Ustawiamy validator na False dla deadlinu
    patch_db_and_validator["validator"].is_valid_deadline.return_value = False
    with pytest.raises(ValueError, match="Deadline musi być datą w przyszłości"):
        task_service.create_task(
            project_id=1,
            title="Przestarzały deadline",
            description="x",
            created_by_id=1,
            assigned_to_id=1,
            deadline="2020-01-01",
            priority="Low"
        )


def test_create_task_default_priority(patch_db_and_validator, task_service):
    """
    Testuje create_task: brak priorytetu w danych
    Oczekuje domyślnego priorytetu "Medium"
    """
    task = task_service.create_task(
        project_id=1,
        title="Brak priorytetu",
        description="x",
        created_by_id=1,
        assigned_to_id=None,
        deadline=None,
        priority=None
    )
    assert task.priority == "Medium"


def test_create_task_db_error(patch_db_and_validator, task_service):
    """
    Testuje create_task: commit rzuca IntegrityError
    Oczekuje rollback i ponowne rzucenie IntegrityError
    """
    patch_db_and_validator["db"].session.commit.side_effect = IntegrityError("s", "p", "o")
    with pytest.raises(IntegrityError):
        task_service.create_task(
            project_id=1,
            title="Test",
            description="x",
            created_by_id=1,
            assigned_to_id=None,
            deadline=None,
            priority=None
        )
    patch_db_and_validator["db"].session.rollback.assert_called_once()


def test_get_tasks_by_project(mocker, task_service):
    """
    Testuje get_tasks_by_project: zwraca listę zadań po project_id
    """
    fake_list = [Mock(), Mock()]
    query = Mock(filter_by=Mock(return_value=Mock(all=Mock(return_value=fake_list))))
    mocker.patch(
        "app.services.task_service.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )
    assert task_service.get_tasks_by_project(5) == fake_list


def test_get_task_by_id_found(mocker, task_service):
    """
    Testuje get_task_by_id: istniejące ID -> zwraca Task
    """
    mock_task = Mock()
    query = Mock(get=Mock(return_value=mock_task))
    mocker.patch(
        "app.services.task_service.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )
    assert task_service.get_task_by_id(123) is mock_task


def test_get_task_by_id_not_found(mocker, task_service):
    """
    Testuje get_task_by_id: brak zadania -> None
    """
    query = Mock(get=Mock(return_value=None))
    mocker.patch(
        "app.services.task_service.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=query
    )
    assert task_service.get_task_by_id(999) is None


def test_update_task_not_found(task_service):
    """
    Testuje update_task: brak zadania -> zwraca None
    """
    task_service.get_task_by_id = lambda x: None
    assert task_service.update_task(1, {}) is None


def test_update_task_success(patch_db_and_validator, mocker, task_service):
    """
    Testuje update_task: poprawne dane -> aktualizacja pól i commit
    """
    mock_task = Mock(
        title="A",
        description="B",
        status="New",
        priority="Low",
        deadline=None
    )
    mocker.patch.object(task_service, "get_task_by_id", return_value=mock_task)
    data = {
        "title": "Zmieniony tytuł",
        "description": "Zmieniony opis",
        "status": "In Progress",
        "priority": "Medium",
        "deadline": "2035-01-01"
    }
    updated = task_service.update_task(task_id=123, data=data)
    assert updated.title == "Zmieniony tytuł"
    assert updated.status == "In Progress"
    patch_db_and_validator["db"].session.commit.assert_called_once()


def test_update_task_invalid_date_format(task_service, mocker):
    """
    Testuje update_task: niepoprawny format daty -> ValueError
    """
    mock_task = Mock()
    mocker.patch.object(task_service, "get_task_by_id", return_value=mock_task)
    with pytest.raises(ValueError, match="Niepoprawny format daty"):
        task_service.update_task(task_id=1, data={"deadline": "zla-data"})


def test_update_task_past_deadline(patch_db_and_validator, mocker, task_service):
    """
    Testuje update_task: validator uważa datę za przeszłą -> ValueError o formacie (aktualne zachowanie)
    """
    patch_db_and_validator["validator"].is_valid_deadline.return_value = False
    mock_task = Mock(deadline=None)
    mocker.patch.object(task_service, "get_task_by_id", return_value=mock_task)
    with pytest.raises(ValueError, match="Niepoprawny format daty"):
        task_service.update_task(task_id=1, data={"deadline": "2020-01-01"})


def test_delete_task_success(mocker, task_service, patch_db_and_validator):
    """
    Testuje delete_task: istniejące zadanie -> usuwa i commit
    """
    mock_task = Mock()
    mocker.patch.object(task_service, "get_task_by_id", return_value=mock_task)
    assert task_service.delete_task(1) is True
    patch_db_and_validator["db"].session.delete.assert_called_once_with(mock_task)
    patch_db_and_validator["db"].session.commit.assert_called_once()


def test_delete_task_not_found(task_service):
    """
    Testuje delete_task: brak zadania -> zwraca False
    """
    task_service.get_task_by_id = lambda x: None
    assert task_service.delete_task(99) is False
