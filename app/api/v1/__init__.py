from app.api.v1.auth import auth_bp
from app.api.v1.projects import projects_bp
from app.api.v1.tasks import tasks_bp
from app.api import api_v1_bp

api_v1_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_v1_bp.register_blueprint(projects_bp, url_prefix='/projects')
api_v1_bp.register_blueprint(tasks_bp, url_prefix='/tasks')