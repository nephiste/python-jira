from app import create_app, db
from app.models import User, Project, Task, Comment
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    db.create_all()

    # Tworzenie użytkownika testowego
    user = User(username='testuser', email='testuser@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    # Tworzenie projektu
    project = Project(
        name='Projekt demonstracyjny',
        description='Projekt stworzony dla demonstracji działania aplikacji.',
        owner_id=user.id
    )
    db.session.add(project)
    db.session.commit()

    # Tworzenie przykładowych zadań o różnych statusach i priorytetach
    tasks = [
        Task(title='Pierwsze zadanie', description='Pierwsze zadanie - wysokiej ważności.',
             project_id=project.id, created_by_id=user.id, assigned_to_id=user.id,
             deadline=datetime.now() + timedelta(days=30), priority='High', status='To Do'),

        Task(title='Drugie zadanie', description='Drugie zadanie - średniej ważności.',
             project_id=project.id, created_by_id=user.id, assigned_to_id=user.id,
             deadline=datetime.now() + timedelta(days=60), priority='Medium', status='In Progress'),

        Task(title='Trzecie zadanie', description='Trzecie zadanie - niskiej ważności.',
             project_id=project.id, created_by_id=user.id, assigned_to_id=user.id,
             deadline=datetime.now() + timedelta(days=90), priority='Low', status='Done'),

        Task(title='Comment Example', description='Zadanie z komentarzami przykładowymi.',
             project_id=project.id, created_by_id=user.id, assigned_to_id=user.id,
             deadline=datetime.now() + timedelta(days=45), priority='Medium', status='To Do')
    ]

    db.session.add_all(tasks)
    db.session.commit()

    # Dodawanie komentarzy do zadania 'Comment Example'
    comment_task = Task.query.filter_by(title='Comment Example').first()

    comments = [
        Comment(task_id=comment_task.id, author_id=user.id, content='Pierwszy przykładowy komentarz.'),
        Comment(task_id=comment_task.id, author_id=user.id, content='Drugi przykładowy komentarz.'),
        Comment(task_id=comment_task.id, author_id=user.id, content='Trzeci przykładowy komentarz.')
    ]

    db.session.add_all(comments)
    db.session.commit()

print('Przykładowe dane zostały pomyślnie załadowane!')
