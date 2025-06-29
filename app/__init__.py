from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.models import db
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate = Migrate(app, db)

    # Rejestracja blueprintów REST API
    from app.routes.auth_routes import auth_bp
    from app.routes.project_routes import project_bp
    from app.routes.task_routes import task_bp
    from app.routes.comment_routes import comment_bp
    from app.routes.status_routes import status_bp
    from app.routes.frontend_routes import frontend_bp
    from app.routes.statistics_routes import stats_bp


    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(project_bp, url_prefix='/api/projects')
    app.register_blueprint(task_bp, url_prefix='/api/tasks')
    app.register_blueprint(comment_bp, url_prefix='/api/comments')
    app.register_blueprint(status_bp, url_prefix='/api/statuses')
    app.register_blueprint(frontend_bp)
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    return app
