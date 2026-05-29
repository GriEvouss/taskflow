import os
from flask import Flask, render_template
from app.config import Config
from app.extensions import db, jwt, migrate, cors


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__, 
                template_folder=os.path.join(BASE_DIR, '..', 'templates'),
                static_folder=os.path.join(BASE_DIR, '..', 'static'))
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    from app.api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp, url_prefix='/api/v1')

    @app.route('/')
    def index():
        return render_template('index.html')

    return app