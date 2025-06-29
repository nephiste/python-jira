import pytest
from unittest.mock import Mock

from app.services.statistics_generator import StatisticsGenerator


@pytest.fixture
# Tworzy instancję StatisticsGenerator przed każdym testem

def stats_gen():
    return StatisticsGenerator()


def test_task_count_by_status_empty(stats_gen):
    """
    Testuje task_count_by_status: pusta lista
    Oczekuje pusty słownik {}
    """
    assert stats_gen.task_count_by_status([]) == {}


def test_task_count_by_status_multiple(stats_gen):
    """
    Testuje task_count_by_status: lista z kilkoma statusami
    Oczekuje podliczenie wystąpień każdego statusu
    """
    tasks = [
        Mock(status="Open"),
        Mock(status="Closed"),
        Mock(status="Open"),
        Mock(status="In Progress"),
        Mock(status="Closed"),
    ]
    counts = stats_gen.task_count_by_status(tasks)
    assert counts == {"Open": 2, "Closed": 2, "In Progress": 1}


def test_generate_global_stats(mocker, stats_gen):
    """
    Testuje generate_global_stats:
    - Task.query.all zwraca listę zadań
    - Project.query.all zwraca listę projektów
    Oczekuje słownik z total_tasks, total_projects oraz status_counts
    """
    fake_tasks = [Mock(status="A"), Mock(status="B"), Mock(status="A")]
    fake_projects = [Mock(), Mock(), Mock(), Mock()]

    task_query = Mock(all=Mock(return_value=fake_tasks))
    proj_query = Mock(all=Mock(return_value=fake_projects))

    mocker.patch(
        "app.services.statistics_generator.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=task_query
    )
    mocker.patch(
        "app.services.statistics_generator.Project.query",
        new_callable=mocker.PropertyMock,
        return_value=proj_query
    )

    result = stats_gen.generate_global_stats()
    assert result["total_tasks"] == 3
    assert result["total_projects"] == 4
    assert result["status_counts"] == {"A": 2, "B": 1}
