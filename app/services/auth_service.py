from flask_jwt_extended import create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    Сервис для работы с аутентификацией и авторизацией.
    Содержит бизнес-логику связанную с пользователями.
    """

    @staticmethod
    def register_user(username: str, email: str, password: str) -> tuple:
        """
        Зарегистрировать нового пользователя.
        Args:
            username: имя пользователя
            email: email пользователя
            password: пароль пользователя
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        if UserRepository.get_by_username(username):
            return False, {'error': 'Username already exists'}, 409

        if UserRepository.get_by_email(email):
            return False, {'error': 'Email already exists'}, 409

        user = UserRepository.create(username, email, password)
        return True, {'message': 'User created successfully', 'user': user.to_dict()}, 201

    @staticmethod
    def authenticate_user(username: str, password: str) -> tuple:
        """
        Аутентифицировать пользователя.
        Args:
            username: имя пользователя
            password: пароль пользователя
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        user = UserRepository.get_by_username(username)

        if not user:
            return False, {'error': 'Invalid username or password'}, 401

        if not UserRepository.verify_password(user, password):
            return False, {'error': 'Invalid username or password'}, 401

        return True, user, 200

    @staticmethod
    def generate_tokens(user_id: int) -> dict:
        """
        Сгенерировать JWT токены для пользователя.
        Args:
            user_id: ID пользователя
        Returns:
            dict: словарь с access и refresh токенами
        """
        access_token = create_access_token(identity=str(user_id))
        refresh_token = create_refresh_token(identity=str(user_id))
        return {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    @staticmethod
    def get_user_by_id(user_id: int) -> tuple:
        """
        Получить пользователя по ID.
        Args:
            user_id: ID пользователя
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        user = UserRepository.get_by_id(user_id)
        if not user:
            return False, {'error': 'User not found'}, 404
        return True, user, 200