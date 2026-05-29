from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError as MarshmallowValidationError
from app.services.task_service import TaskService
from app.schemas.task_schema import TaskCreateSchema, TaskUpdateSchema

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/project/<int:project_id>', methods=['GET'])
@jwt_required()
def get_project_tasks(project_id):
    """Получить все задачи проекта с подзадачами."""
    user_id = int(get_jwt_identity())
    success, result, status = TaskService.get_project_tasks(project_id, user_id)

    if not success:
        return jsonify(result), status

    return jsonify({'tasks': result}), status


@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Создать задачу или подзадачу."""
    user_id = int(get_jwt_identity())
    schema = TaskCreateSchema()

    try:
        data = schema.load(request.get_json())
    except MarshmallowValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400

    success, result, status = TaskService.create_task(
        title=data['title'],
        description=data.get('description', ''),
        project_id=data.get('project_id'),
        assignee_id=data.get('assignee_id'),
        status=data.get('status', 'todo'),
        parent_id=data.get('parent_id')
    )

    return jsonify(result.to_dict() if hasattr(result, 'to_dict') else result), status


@tasks_bp.route('/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Получить конкретную задачу."""
    success, result, status = TaskService.get_task(task_id)

    if not success:
        return jsonify(result), status

    return jsonify({'task': result.to_dict() if hasattr(result, 'to_dict') else result}), status


@tasks_bp.route('/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Обновить задачу."""
    user_id = int(get_jwt_identity())
    schema = TaskUpdateSchema()

    try:
        data = schema.load(request.get_json())
    except MarshmallowValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400

    success, result, status = TaskService.update_task(task_id, user_id, **data)

    return jsonify(result if isinstance(result, dict) else result.to_dict()), status


@tasks_bp.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Удалить задачу и все подзадачи."""
    user_id = int(get_jwt_identity())
    success, result, status = TaskService.delete_task(task_id, user_id)

    return jsonify(result), status