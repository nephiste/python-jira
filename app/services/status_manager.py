from app.models import Task, TaskStatusHistory, db
from datetime import datetime

class StatusManager:
    def change_status(self, task_id, new_status, changed_by_id):
        task = Task.query.get(task_id)
        if not task:
            raise ValueError("Zadanie o podanym ID nie istnieje.")

        old_status = task.status
        task.status = new_status

        history = TaskStatusHistory(
            task_id=task_id,
            old_status=old_status,
            new_status=new_status,
            changed_by_id=changed_by_id,
            changed_at=datetime.utcnow()
        )

        try:
            db.session.commit()  # update task
            db.session.add(history)
            db.session.commit()  # save history
        except Exception as e:
            db.session.rollback()
            raise e

        return task

    def get_history_for_task(self, task_id):
        return TaskStatusHistory.query.filter_by(task_id=task_id).order_by(TaskStatusHistory.changed_at.desc()).all()
