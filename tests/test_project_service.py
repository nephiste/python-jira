import pytest
from datetime import datetime
from unittest.mock import Mock, ANY
from sqlalchemy.exc import SQLAlchemyError

from app.services.project_service import ProjectService


@pytest.fixture(autouse=True)
# Podmieniamy `db.session` i klasę `Project`, by izolować testowaną logikę od bazy

def patch_db_and_Project(mocker):
    db_mock = mocker.patch("app.services.project_service.db", autospec=True)
    db_mock.session = mocker.Mock()
    project_cls = mocker.patch("app.services.project_service.Project", autospec=True)
    instance = project_cls.return_value
    return {"db": db_mock, "Project": project_cls, "instance": instance}


@pytest.fixture
# Tworzy instancję serwisu projektów

def project_service():
    return ProjectService()


def test_create_project_success(patch_db_and_Project, project_service):
    """
    Testuje create_project: sukces tworzenia nowego projektu
    - Sprawdza, że wywołano konstruktor Project z poprawnymi argumentami
    - Dodaje do sesji i commit
    """
    res = project_service.create_project(user_id=42, name="My Project", description="Desc")
    assert res is patch_db_and_Project["instance"]
    patch_db_and_Project["Project"].assert_called_once_with(
        name="My Project", description="Desc", owner_id=42, created_at=ANY
    )
    patch_db_and_Project["db"].session.add.assert_called_once_with(res)
    patch_db_and_Project["db"].session.commit.assert_called_once()


def test_create_project_default_description(patch_db_and_Project, project_service):
    """
    Testuje create_project: gdy description=None, ustawia pusty string
    """
    project_service.create_project(user_id=1, name="P", description=None)
    patch_db_and_Project["Project"].assert_called_once_with(
        name="P", description="", owner_id=1, created_at=ANY
    )


def test_create_project_missing_fields(project_service):
    """
    Testuje create_project: brak user_id lub nazwy -> ValueError
    """
    with pytest.raises(ValueError, match="Brakuje wymaganych danych"):
        project_service.create_project(user_id=None, name="X", description="D")
    with pytest.raises(ValueError, match="Brakuje wymaganych danych"):
        project_service.create_project(user_id=1, name="", description="D")


def test_create_project_db_error(patch_db_and_Project, project_service):
    """
    Testuje create_project: commit rzuca wyjątek SQLAlchemyError -> rollback + wyjątek
    """
    patch_db_and_Project["db"].session.commit.side_effect = SQLAlchemyError("fail")
    with pytest.raises(SQLAlchemyError):
        project_service.create_project(user_id=1, name="X", description="D")
    patch_db_and_Project["db"].session.rollback.assert_called_once()


def test_get_projects_by_owner(project_service):
    """
    Testuje get_projects_by_owner: zwraca listę projektów dla danego owner_id
    """
    fake = [Mock(), Mock()]
    query = Mock(filter_by=Mock(return_value=Mock(all=Mock(return_value=fake))))
    import app.services.project_service as ps_mod
    ps_mod.Project.query = query
    assert project_service.get_projects_by_owner(owner_id=7) == fake


def test_get_project_by_id_found(project_service):
    """
    Testuje get_project_by_id: istniejący projekt -> zwraca obiekt
    """
    mock_proj = Mock()
    query = Mock(get=Mock(return_value=mock_proj))
    import app.services.project_service as ps_mod
    ps_mod.Project.query = query
    assert project_service.get_project_by_id(99) is mock_proj


def test_get_project_by_id_not_found(project_service):
    """
    Testuje get_project_by_id: brak projektu -> zwraca None
    """
    query = Mock(get=Mock(return_value=None))
    import app.services.project_service as ps_mod
    ps_mod.Project.query = query
    assert project_service.get_project_by_id(123) is None


def test_update_project_not_found(project_service):
    """
    Testuje update_project: brak projektu -> None
    """
    project_service.get_project_by_id = lambda x: None
    assert project_service.update_project(1, {"name": "X"}) is None


def test_update_project_success(patch_db_and_Project, project_service):
    """
    Testuje update_project: aktualizacja pól + commit
    """
    mock_proj = patch_db_and_Project["instance"]
    mock_proj.name = "Old"
    mock_proj.description = "Desc"
    project_service.get_project_by_id = lambda x: mock_proj
    data = {"name": "New", "description": "NewDesc"}
    updated = project_service.update_project(project_id=5, data=data)
    assert updated.name == "New"
    assert updated.description == "NewDesc"
    patch_db_and_Project["db"].session.commit.assert_called_once()


def test_delete_project_success(patch_db_and_Project, project_service):
    """
    Testuje delete_project: istniejący projekt -> usuwa + commit
    """
    mock_proj = patch_db_and_Project["instance"]
    project_service.get_project_by_id = lambda x: mock_proj
    assert project_service.delete_project(2) is True
    patch_db_and_Project["db"].session.delete.assert_called_once_with(mock_proj)
    patch_db_and_Project["db"].session.commit.assert_called_once()


def test_delete_project_not_found(project_service):
    """
    Testuje delete_project: brak projektu -> False
    """
    project_service.get_project_by_id = lambda x: None
    assert project_service.delete_project(999) is False
