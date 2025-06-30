import pytest
from datetime import datetime
from io import StringIO
import csv
from unittest.mock import Mock

from app.services.csv_exporter import CSVExporter


@pytest.fixture
# Fixture zwraca instancję eksportera CSV przed każdym testem

def exporter():
    return CSVExporter()


@pytest.fixture
# Fixture zwraca stałą datę do testów (ułatwia porównania)

def fixed_dt():
    return datetime(2025, 6, 29, 12, 0, 0)


def test_export_tasks_for_project_not_found(mocker, exporter):
    """
    Testuje export_tasks_for_project: gdy projekt nie istnieje
    Oczekuje zwrócenia None
    """
    proj_query = Mock(get=Mock(return_value=None))
    mocker.patch(
        "app.services.csv_exporter.Project.query",
        new_callable=mocker.PropertyMock,
        return_value=proj_query
    )
    assert exporter.export_tasks_for_project(1) is None


def test_export_tasks_for_project_no_tasks(mocker, exporter, fixed_dt):
    """
    Testuje export_tasks_for_project: projekt istnieje, brak zadań
    Oczekuje CSV z nagłówkiem projektu i pustą sekcją zadań
    """
    # Przygotowanie obiektu projektu z atrybutami
    project = Mock()
    project.id = 1
    project.name = "Proj"
    project.description = "Desc"
    project.created_at = fixed_dt

    proj_query = Mock(get=Mock(return_value=project))
    mocker.patch(
        "app.services.csv_exporter.Project.query",
        new_callable=mocker.PropertyMock,
        return_value=proj_query
    )

    # Task.query.filter_by(...).all() -> []
    task_query = Mock(filter_by=Mock(return_value=Mock(all=Mock(return_value=[]))))
    mocker.patch(
        "app.services.csv_exporter.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=task_query
    )

    output = exporter.export_tasks_for_project(1)
    rows = list(csv.reader(StringIO(output), delimiter=";"))

    # Nagłówek projektu
    assert rows[0] == ["Projekt: ID", "Nazwa", "Opis", "Data utworzenia"]
    # Dane projektu
    assert rows[1] == ["1", "Proj", "Desc", fixed_dt.isoformat()]
    # Pusta linia
    assert rows[2] == []
    # Nagłówek zadań
    assert rows[3] == ["Zadanie ID", "Tytuł", "Opis", "Status", "Priorytet", "Deadline", "Utworzone"]
    # Sprawdzenie długości: tylko 4 wiersze
    assert len(rows) == 4


def test_export_tasks_for_project_with_tasks(mocker, exporter, fixed_dt):
    """
    Testuje export_tasks_for_project: projekt z dwoma zadaniami
    Oczekuje CSV z dwoma kolejnymi wierszami danych zadań
    """
    # Przygotowanie obiektu projektu
    project = Mock()
    project.id = 2
    project.name = "P2"
    project.description = "D2"
    project.created_at = fixed_dt

    proj_query = Mock(get=Mock(return_value=project))
    mocker.patch(
        "app.services.csv_exporter.Project.query",
        new_callable=mocker.PropertyMock,
        return_value=proj_query
    )

    # Przygotowanie dwóch zadań
    d1 = Mock()
    d1.id = 10
    d1.title = "T1"
    d1.description = "Desc1"
    d1.status = "Open"
    d1.priority = "High"
    d1.deadline = None
    d1.created_at = fixed_dt

    d2 = Mock()
    d2.id = 11
    d2.title = "T2"
    d2.description = "Desc2"
    d2.status = "Closed"
    d2.priority = "Low"
    d2.deadline = datetime(2025, 7, 1, 8, 30, 0)
    d2.created_at = fixed_dt

    task_query = Mock(filter_by=Mock(return_value=Mock(all=Mock(return_value=[d1, d2]))))
    mocker.patch(
        "app.services.csv_exporter.Task.query",
        new_callable=mocker.PropertyMock,
        return_value=task_query
    )

    output = exporter.export_tasks_for_project(2)
    rows = list(csv.reader(StringIO(output), delimiter=";"))

    # Sprawdzenie danych pierwszego zadania (brak deadline)
    assert rows[4] == ["10", "T1", "Desc1", "Open", "High", "", fixed_dt.isoformat()]
    # Sprawdzenie danych drugiego zadania (z deadline)
    assert rows[5] == [
        "11", "T2", "Desc2", "Closed", "Low",
        d2.deadline.isoformat(), fixed_dt.isoformat()
    ]
