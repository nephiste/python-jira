from flask import Blueprint, request, jsonify, Response
from app.models import db, Task
from datetime import datetime
from app.services.csv_exporter import CSVExporter

task_bp = Blueprint('tasks', __name__)

@task_bp.route('/', methods=['POST'])
def create_task():
    data = request.get_json()
    title = data.get('title')
    description = data.get('description')
    project_id = data.get('project_id')
    created_by_id = data.get('created_by_id')
    assigned_to_id = data.get('assigned_to_id')
    deadline_str = data.get('deadline')
    priority = data.get('priority', 'Medium')

    if not all([title, project_id, created_by_id]):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d") if deadline_str else None
    except ValueError:
        return jsonify({'error': 'Invalid deadline format. Use YYYY-MM-DD.'}), 400

    task = Task(
        title=title,
        description=description,
        project_id=int(project_id),
        created_by_id=int(created_by_id),
        assigned_to_id=int(assigned_to_id) if assigned_to_id else None,
        deadline=deadline,
        priority=priority
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({'message': 'Task created', 'task_id': task.id}), 201

@task_bp.route('/project/<int:project_id>', methods=['GET'])
def get_tasks_by_project(project_id):
    tasks = Task.query.filter_by(project_id=project_id).all()
    result = [
        {
            'id': t.id,
            'title': t.title,
            'status': t.status,
            'priority': t.priority,
            'assigned_to': t.assigned_to_id,
            'deadline': t.deadline.isoformat() if t.deadline else None
        }
        for t in tasks
    ]
    return jsonify(result), 200

@task_bp.route('/<int:id>', methods=['GET'])
def get_task(id):
    task = Task.query.get(id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify({
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'deadline': task.deadline.isoformat() if task.deadline else None,
        'created_by_id': task.created_by_id,
        'assigned_to_id': task.assigned_to_id,
        'project_id': task.project_id,
        'created_at': task.created_at.isoformat()
    }), 200

@task_bp.route('/export/project/<int:project_id>', methods=['GET'])
def export_tasks_csv(project_id):
    exporter = CSVExporter()
    csv_data = exporter.export_tasks_for_project(project_id)
    if not csv_data:
        return jsonify({'error': 'Project not found'}), 404

    return Response(
        csv_data,
        mimetype='text/csv',
        headers={"Content-disposition": f"attachment; filename=project_{project_id}_tasks.csv"}
    )
