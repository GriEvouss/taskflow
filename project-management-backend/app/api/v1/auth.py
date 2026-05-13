from flask import Blueprint, request, jsonify
from marshmallow import ValidationError as MarshmallowValidationError
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserCreateSchema, UserLoginSchema

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Регистрация нового пользователя.
    Принимает JSON: username, email, password.
    """
    schema = UserCreateSchema()

    try:
        data = schema.load(request.get_json())
    except MarshmallowValidationError as e:
        print(f"Validation error: {e.messages}")
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400

    success, result, status = AuthService.register_user(
        username=data['username'],
        email=data['email'],
        password=data['password']
    )

    return jsonify(result), status


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Вход пользователя.
    Принимает JSON: username, password.
    Возвращает access и refresh токены.
    """
    schema = UserLoginSchema()

    try:
        data = schema.load(request.get_json())
    except MarshmallowValidationError as e:
        return jsonify({'error': 'Validation error', 'details': e.messages}), 400

    success, user, status = AuthService.authenticate_user(
        username=data['username'],
        password=data['password']
    )

    if not success:
        return jsonify(user), status

    tokens = AuthService.generate_tokens(user.id)

    return jsonify({
        'access_token': tokens['access_token'],
        'refresh_token': tokens['refresh_token'],
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value if hasattr(user.role, 'value') else 'user'
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Обновление access токена.
    Принимает refresh токен в заголовке Authorization.
    """
    from flask_jwt_extended import get_jwt_identity, create_access_token

    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)

    return jsonify({'access_token': access_token}), 200