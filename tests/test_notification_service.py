import pytest
from datetime import datetime
from unittest.mock import Mock

import app.services.notification_service as ns_mod
from app.services.notification_service import NotificationService


@pytest.fixture(autouse=True)
# Zamraża czas, żeby logi były deterministyczne (stały timestamp)

def fixed_datetime(monkeypatch):
    fixed = datetime(2025, 6, 29, 12, 0, 0)
    # Podmieniamy datetime.now() w module na zwracające 'fixed'
    monkeypatch.setattr(ns_mod, "datetime", Mock(now=Mock(return_value=fixed)))
    return fixed


def test_log_notification_without_extra(capsys, fixed_datetime):
    """
    Testuje log_notification: bez dodatkowych szczegółów
    Oczekuje linię: [timestamp] Notification: user=..., task=..., type=...
    """
    svc = NotificationService()
    svc.log_notification(user_id=1, task_id=2, message_type="typeA")
    captured = capsys.readouterr().out.strip()
    expected = f"[{fixed_datetime.isoformat()}] Notification: user=1, task=2, type=typeA"
    assert captured == expected


def test_log_notification_with_extra(capsys, fixed_datetime):
    """
    Testuje log_notification: z parametrem extra
    Oczekuje: ", details=..." na końcu logu
    """
    svc = NotificationService()
    svc.log_notification(user_id=3, task_id=4, message_type="typeB", extra="details")
    captured = capsys.readouterr().out.strip()
    expected = (
        f"[{fixed_datetime.isoformat()}] Notification: user=3, task=4, type=typeB"
        f", details=details"
    )
    assert captured == expected


def test_send_task_assignment_notification(mocker):
    """
    Testuje send_task_assignment_notification: delegacja do log_notification
    """
    svc = NotificationService()
    svc.log_notification = Mock()
    svc.send_task_assignment_notification(user_id=5, task_id=6)
    svc.log_notification.assert_called_once_with(5, 6, "task_assigned")


def test_send_status_change_notification(mocker):
    """
    Testuje send_status_change_notification: deleguje z extra "old -> new"
    """
    svc = NotificationService()
    svc.log_notification = Mock()
    svc.send_status_change_notification(user_id=7, task_id=8, old_status="X", new_status="Y")
    svc.log_notification.assert_called_once_with(
        7, 8, "status_changed", extra="X -> Y"
    )


def test_send_comment_notification(mocker):
    """
    Testuje send_comment_notification: delegacja do log_notification
    """
    svc = NotificationService()
    svc.log_notification = Mock()
    svc.send_comment_notification(user_id=9, task_id=10)
    svc.log_notification.assert_called_once_with(9, 10, "new_comment")
