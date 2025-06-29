from flask import Blueprint, request, jsonify
from app.models import db, Task, TaskStatusHistory

status_bp = Blueprint('statuses', __name__)

VALID_STATUSES = {"To Do", "In Progress", "Done"}

@status_bp.route('/change', methods=['POST'])
def change_status():
    data = request.get_json()
    task_id = data.get('task_id')
    new_status = data.get('new_status')
    changed_by_id = data.get('changed_by_id')

    if not task_id or not new_status or not changed_by_id:
        return jsonify({'error': 'Missing required fields'}), 400

    if new_status not in VALID_STATUSES:
        return jsonify({'error': f'Invalid status. Allowed: {", ".join(VALID_STATUSES)}'}), 400

    task = Task.query.get(task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    old_status = task.status
    task.status = new_status
    db.session.commit()

    history = TaskStatusHistory(
        task_id=task_id,
        old_status=old_status,
        new_status=new_status,
        changed_by_id=changed_by_id
    )
    db.session.add(history)
    db.session.commit()

    return jsonify({'message': 'Status changed'}), 200


@status_bp.route('/history/<int:task_id>', methods=['GET'])
def get_status_history(task_id):
    history = TaskStatusHistory.query.filter_by(task_id=task_id) \
                                     .order_by(TaskStatusHistory.changed_at.asc()) \
                                     .all()

    result = [
        {
            'id': h.id,
            'old_status': h.old_status,
            'new_status': h.new_status,
            'changed_by_id': h.changed_by_id,
            'changed_at': h.changed_at.isoformat()
        }
        for h in history
    ]
    return jsonify(result), 200
