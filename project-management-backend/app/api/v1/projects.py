from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError
from app.services.project_service import ProjectService
from app.schemas.project_schema import ProjectCreateSchema, ProjectUpdateSchema

projects_bp = Blueprint('projects', __name__)


@projects_bp.route('', methods=['GET'])
@jwt_required()
def get_projects():
    """
    Получить все проекты текущего пользователя.
    """
    user_id = int(get_jwt_identity())
    success, projects, status = ProjectService.get_user_projects(user_id)

    return jsonify({
        'projects': [
            {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'created_at': p.created_at.isoformat() if p.created_at else None
            }
            for p in projects
        ]
    }), status


@projects_bp.route('', methods=['POST'])
@jwt_required()
def create_project():
    """
    Создать новый проект.
    Принимает JSON: name, description.
    """
    user_id = int(get_jwt_identity())
    schema = ProjectCreateSchema()

    try:
        data = schema.load(request.get_json())
    except MarshmallowValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400

    success, result, status = ProjectService.create_project(
        name=data['name'],
        description=data.get('description', ''),
        owner_id=user_id
    )

    if not success:
        return jsonify(result), status

    return jsonify({
        'project': {
            'id': result.id,
            'name': result.name,
            'description': result.description,
            'created_at': result.created_at.isoformat() if result.created_at else None
        }
    }), status


@projects_bp.route('/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project(project_id):
    """
    Получить конкретный проект.
    """
    user_id = int(get_jwt_identity())
    success, result, status = ProjectService.get_project(project_id, user_id)

    if not success:
        return jsonify(result), status

    return jsonify({
        'project': {
            'id': result.id,
            'name': result.name,
            'description': result.description,
            'owner_id': result.owner_id,
            'owner_username': result.owner.username if result.owner else None,
            'created_at': result.created_at.isoformat() if result.created_at else None,
            'updated_at': result.updated_at.isoformat() if result.updated_at else None
        }
    }), status


@projects_bp.route('/<int:project_id>', methods=['PUT'])
@jwt_required()
def update_project(project_id):
    """
    Обновить проект.
    Принимает JSON: name, description.
    """
    user_id = int(get_jwt_identity())
    schema = ProjectUpdateSchema()

    try:
        data = schema.load(request.get_json())
    except MarshmallowValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400

    success, result, status = ProjectService.update_project(
        project_id=project_id,
        user_id=user_id,
        **data
    )

    if not success:
        return jsonify(result), status

    return jsonify({
        'project': {
            'id': result.id,
            'name': result.name,
            'description': result.description,
            'updated_at': result.updated_at.isoformat() if result.updated_at else None
        }
    }), status


@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@jwt_required()
def delete_project(project_id):
    """
    Удалить проект.
    """
    user_id = int(get_jwt_identity())
    success, result, status = ProjectService.delete_project(project_id, user_id)

    return jsonify(result), status