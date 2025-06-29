from app.models import User, db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

class UserService:
    def register_user(self, username, email, password):
        if not username or not email or not password:
            raise ValueError("Wszystkie pola są wymagane.")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            raise ValueError("Użytkownik o podanej nazwie lub emailu już istnieje.")

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Błąd przy zapisie użytkownika do bazy.")

        return user

    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    def get_user_by_id(self, user_id):
        return User.query.get(user_id)

    def get_all_users(self):
        return User.query.all()

    def delete_user(self, user_id):
        user = self.get_user_by_id(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
