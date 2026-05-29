import os
from app import create_app
from app.extensions import db
from app.version import VERSION

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


@app.route('/api/version')
def version():
    from flask import jsonify
    return jsonify({'version': VERSION, 'environment': os.environ.get('FLASK_ENV', 'production')})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    debug = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=5000)