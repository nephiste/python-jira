import csv
from io import StringIO
from app.models import Task, Project

class CSVExporter:
    def export_tasks_for_project(self, project_id):
        project = Project.query.get(project_id)
        if not project:
            return None

        tasks = Task.query.filter_by(project_id=project_id).all()

        si = StringIO()
        writer = csv.writer(si, delimiter=';')

        # Informacje o projekcie
        writer.writerow(["Projekt: ID", "Nazwa", "Opis", "Data utworzenia"])
        writer.writerow([project.id, project.name, project.description, project.created_at.isoformat()])
        writer.writerow([])  # pusta linia oddzielająca

        # Nagłówek zadań
        writer.writerow(["Zadanie ID", "Tytuł", "Opis", "Status", "Priorytet", "Deadline", "Utworzone"])
        for task in tasks:
            writer.writerow([
                task.id,
                task.title,
                task.description,
                task.status,
                task.priority,
                task.deadline.isoformat() if task.deadline else "",
                task.created_at.isoformat()
            ])

        return si.getvalue()
