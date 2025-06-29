from app.models import Task, db
from datetime import datetime
from app.services.deadline_validator import DeadlineValidator

class TaskService:
    def __init__(self):
        self.validator = DeadlineValidator()

    def create_task(self, project_id, title, description, created_by_id, assigned_to_id, deadline, priority):
        if not title or not project_id or not created_by_id:
            raise ValueError("Brak wymaganych pól: title, project_id, created_by_id.")

        try:
            deadline_dt = datetime.strptime(deadline, "%Y-%m-%d") if deadline else None
        except ValueError:
            raise ValueError("Niepoprawny format daty. Użyj YYYY-MM-DD.")

        if deadline_dt and not self.validator.is_valid_deadline(deadline_dt):
            raise ValueError("Deadline musi być datą w przyszłości.")

        task = Task(
            title=title,
            description=description,
            project_id=int(project_id),
            created_by_id=int(created_by_id),
            assigned_to_id=int(assigned_to_id) if assigned_to_id else None,
            deadline=deadline_dt,
            priority=priority or 'Medium'
        )
        db.session.add(task)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return task

    def get_tasks_by_project(self, project_id):
        return Task.query.filter_by(project_id=project_id).all()

    def get_task_by_id(self, task_id):
        return Task.query.get(task_id)

    def update_task(self, task_id, data):
        task = self.get_task_by_id(task_id)
        if not task:
            return None

        task.title = data.get("title", task.title)
        task.description = data.get("description", task.description)
        task.status = data.get("status", task.status)
        task.priority = data.get("priority", task.priority)

        deadline = data.get("deadline")
        if deadline:
            try:
                deadline_dt = datetime.strptime(deadline, "%Y-%m-%d")
                if not self.validator.is_valid_deadline(deadline_dt):
                    raise ValueError("Deadline musi być datą w przyszłości.")
                task.deadline = deadline_dt
            except ValueError:
                raise ValueError("Niepoprawny format daty.")

        db.session.commit()
        return task

    def delete_task(self, task_id):
        task = self.get_task_by_id(task_id)
        if task:
            db.session.delete(task)
            db.session.commit()
            return True
        return False
