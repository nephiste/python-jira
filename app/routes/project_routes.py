from flask import Blueprint, request, jsonify
from app.models import db, Project

project_bp = Blueprint('projects', __name__)

@project_bp.route('/', methods=['POST'])
def create_project():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    owner_id = data.get('owner_id')

    if not name or not owner_id:
        return jsonify({'error': 'Missing name or owner_id'}), 400

    project = Project(name=name, description=description, owner_id=owner_id)
    db.session.add(project)
    db.session.commit()

    return jsonify({'message': 'Project created', 'project_id': project.id}), 201

@project_bp.route('/<int:owner_id>', methods=['GET'])
def list_projects(owner_id):
    projects = Project.query.filter_by(owner_id=owner_id).all()
    result = [
        {
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'created_at': p.created_at.isoformat() if p.created_at else None
        }
        for p in projects
    ]
    return jsonify(result), 200

@project_bp.route('/get/<int:project_id>', methods=['GET'])
def get_project_by_id(project_id):
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Projekt nie istnieje'}), 404

    return jsonify({
        'id': project.id,
        'name': project.name,
        'description': project.description,
        'created_at': project.created_at.isoformat() if project.created_at else None,
        'owner_id': project.owner_id
    }), 200
