import pytest
from unittest.mock import Mock

import app.services.comment_service as cs_mod
from app.services.comment_service import CommentService


@pytest.fixture(autouse=True)
# Przygotowuje i podmienia obiekt db oraz klasę Comment przed każdym testem
# Umożliwia izolację testów logiki dodawania i usuwania komentarzy od bazy danych

def patch_db_and_Comment(mocker):
    db_mock = mocker.patch.object(cs_mod, "db", autospec=True)
    db_mock.session = mocker.Mock()
    comment_cls = mocker.patch.object(cs_mod, "Comment", autospec=True)
    return {"db": db_mock, "Comment": comment_cls}


@pytest.fixture
# Zwraca instancję serwisu komentarzy

def comment_service():
    return CommentService()


def test_add_comment_success(patch_db_and_Comment, comment_service):
    """
    Testuje add_comment: Sukces dodania komentarza
    Oczekuje wywołania session.add i session.commit
    """
    inst = patch_db_and_Comment["Comment"].return_value
    result = comment_service.add_comment(task_id=5, user_id=10, content="Hello")
    assert result is inst
    patch_db_and_Comment["db"].session.add.assert_called_once_with(inst)
    patch_db_and_Comment["db"].session.commit.assert_called_once()


@pytest.mark.parametrize("task_id,user_id,content", [
    (None, 1, "c"), (1, None, "c"), (1, 1, "")
])
def test_add_comment_missing_fields(comment_service, task_id, user_id, content):
    """
    Testuje add_comment: Brak wymaganych danych
    Oczekuje ValueError przy pustych polach
    """
    with pytest.raises(ValueError, match="Brakuje wymaganych danych"):
        comment_service.add_comment(task_id=task_id, user_id=user_id, content=content)


def test_add_comment_db_error(patch_db_and_Comment, comment_service):
    """
    Testuje add_comment: Błąd zapisu do bazy
    Oczekuje rollback po wyjątku commit
    """
    patch_db_and_Comment["db"].session.commit.side_effect = Exception("fail")
    with pytest.raises(Exception):
        comment_service.add_comment(task_id=1, user_id=1, content="X")
    patch_db_and_Comment["db"].session.rollback.assert_called_once()


def test_get_comments(comment_service):
    """
    Testuje get_comments: Pobranie listy komentarzy
    Oczekuje wywołania filter_by i order_by, zwraca listę
    """
    fake = [Mock(), Mock()]
    q = Mock()
    q.filter_by.return_value = q
    q.order_by.return_value = q
    q.all.return_value = fake

    cs_mod.Comment.query = q

    result = comment_service.get_comments(task_id=7)
    assert result == fake
    q.filter_by.assert_called_once_with(task_id=7)
    q.order_by.assert_called_once()


def test_delete_comment_not_found(comment_service):
    """
    Testuje delete_comment: brak komentarza
    Oczekuje False gdy query.get zwraca None
    """
    cs_mod.Comment.query = Mock(get=Mock(return_value=None))
    assert comment_service.delete_comment(comment_id=1, user_id=10) is False


def test_delete_comment_wrong_user(patch_db_and_Comment, comment_service):
    """
    Testuje delete_comment: nieautoryzowany user
    Oczekuje False gdy user_id != author_id
    """
    inst = patch_db_and_Comment["Comment"].return_value
    inst.author_id = 5
    cs_mod.Comment.query = Mock(get=Mock(return_value=inst))
    assert comment_service.delete_comment(comment_id=1, user_id=10) is False


def test_delete_comment_success_no_user(patch_db_and_Comment, comment_service):
    """
    Testuje delete_comment: sukces usunięcia bez określonego user_id
    Oczekuje remove + commit
    """
    inst = patch_db_and_Comment["Comment"].return_value
    cs_mod.Comment.query = Mock(get=Mock(return_value=inst))
    assert comment_service.delete_comment(comment_id=2) is True
    patch_db_and_Comment["db"].session.delete.assert_called_once_with(inst)
    patch_db_and_Comment["db"].session.commit.assert_called_once()


def test_delete_comment_success_with_user(patch_db_and_Comment, comment_service):
    """
    Testuje delete_comment: sukces usunięcia przez autora
    Oczekuje remove + commit gdy user_id == author_id
    """
    inst = patch_db_and_Comment["Comment"].return_value
    inst.author_id = 42
    cs_mod.Comment.query = Mock(get=Mock(return_value=inst))
    assert comment_service.delete_comment(comment_id=3, user_id=42) is True
    patch_db_and_Comment["db"].session.delete.assert_called_once_with(inst)
    patch_db_and_Comment["db"].session.commit.assert_called_once()


def test_get_comment_by_id(comment_service):
    """
    Testuje get_comment_by_id: pobranie komentarza po ID
    Oczekuje zwrócenie obiektu Comment lub None
    """
    inst = Mock()
    cs_mod.Comment.query = Mock(get=Mock(return_value=inst))
    assert comment_service.get_comment_by_id(123) is inst
