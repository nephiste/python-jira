from flask import Blueprint, render_template

frontend_bp = Blueprint('frontend', __name__)

@frontend_bp.route('/')
def index():
    return render_template('index.html')

@frontend_bp.route('/index.html')
def indexh():
    return render_template('index.html')


@frontend_bp.route('/project.html')
def project():
    return render_template('project.html')

@frontend_bp.route('/task.html')
def task():
    return render_template('task.html')

@frontend_bp.route('/statistics.html')
def statistics():
    return render_template('statistics.html')

@frontend_bp.route('/comments.html')
def comments():
    return render_template('comments.html')

@frontend_bp.route('/statuses.html')
def statuses():
    return render_template('statuses.html')
