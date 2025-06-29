from flask import Blueprint, request, jsonify
from app.models import db, Comment, User

comment_bp = Blueprint('comments', __name__)


@comment_bp.route('/', methods=['POST'])
def add_comment():
    data = request.get_json()
    task_id = data.get('task_id')
    user_id = data.get('user_id') or data.get('author_id')  # Obsługuje oba klucze
    content = data.get('content')

    if not all([task_id, user_id, content]):
        return jsonify({'error': 'Missing fields'}), 400

    comment = Comment(task_id=task_id, author_id=user_id, content=content)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'Comment added', 'comment_id': comment.id}), 201


@comment_bp.route('/task/<int:task_id>', methods=['GET'])
def get_comments(task_id):
    comments = Comment.query.filter_by(task_id=task_id).all()

    result = []
    for c in comments:
        author = User.query.get(c.author_id)
        result.append({
            'id': c.id,
            'author_id': c.author_id,
            'author_name': author.username if author else f"Użytkownik {c.author_id}",
            'content': c.content,
            'created_at': c.created_at.isoformat()
        })

    return jsonify(result), 200
