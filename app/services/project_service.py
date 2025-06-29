from app.models import Project, db
from datetime import datetime

class ProjectService:
    def create_project(self, user_id, name, description):
        if not name or not user_id:
            raise ValueError("Brakuje wymaganych danych: name, user_id.")

        project = Project(
            name=name,
            description=description or '',
            owner_id=user_id,
            created_at=datetime.utcnow()
        )
        db.session.add(project)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        return project

    def get_projects_by_owner(self, owner_id):
        return Project.query.filter_by(owner_id=owner_id).all()

    def get_project_by_id(self, project_id):
        return Project.query.get(project_id)

    def update_project(self, project_id, data):
        project = self.get_project_by_id(project_id)
        if not project:
            return None

        project.name = data.get("name", project.name)
        project.description = data.get("description", project.description)
        db.session.commit()
        return project

    def delete_project(self, project_id):
        project = self.get_project_by_id(project_id)
        if project:
            db.session.delete(project)
            db.session.commit()
            return True
        return False
