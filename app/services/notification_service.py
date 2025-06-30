from datetime import datetime

class NotificationService:
    def log_notification(self, user_id, task_id, message_type, extra=None):
        timestamp = datetime.now().isoformat()
        log = f"[{timestamp}] Notification: user={user_id}, task={task_id}, type={message_type}"
        if extra:
            log += f", details={extra}"
        print(log)

    def send_task_assignment_notification(self, user_id, task_id):
        self.log_notification(user_id, task_id, "task_assigned")

    def send_status_change_notification(self, user_id, task_id, old_status, new_status):
        self.log_notification(
            user_id,
            task_id,
            "status_changed",
            extra=f"{old_status} -> {new_status}"
        )

    def send_comment_notification(self, user_id, task_id):
        self.log_notification(user_id, task_id, "new_comment")
