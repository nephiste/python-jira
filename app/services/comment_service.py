from app.models import Comment, db
from datetime import datetime

class CommentService:
    def add_comment(self, task_id, user_id, content):
        if not content or not task_id or not user_id:
            raise ValueError("Brakuje wymaganych danych.")

        comment = Comment(
            task_id=task_id,
            author_id=user_id,
            content=content,
            created_at=datetime.utcnow()
        )

        db.session.add(comment)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return comment

    def get_comments(self, task_id):
        return Comment.query.filter_by(task_id=task_id).order_by(Comment.created_at.desc()).all()

    def delete_comment(self, comment_id, user_id=None):
        comment = Comment.query.get(comment_id)
        if not comment:
            return False
        if user_id and comment.author_id != user_id:
            return False  # tylko autor może usunąć swój komentarz
        db.session.delete(comment)
        db.session.commit()
        return True

    def get_comment_by_id(self, comment_id):
        return Comment.query.get(comment_id)
