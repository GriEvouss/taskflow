from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash


class UserRepository:
    """
    Репозиторий для работы с пользователями.
    Реализует CRUD операции для модели User.
    """

    @staticmethod
    def create(username: str, email: str, password: str, role: str = 'user') -> User:
        """
        Создать нового пользователя.
        Args:
            username: имя пользователя
            email: email пользователя
            password: пароль пользователя
            role: роль пользователя (user/admin)
        Returns:
            User: созданный объект пользователя
        """
        from app.models.user import UserRole
        user = User(username=username, email=email)
        user.password_hash = generate_password_hash(password)
        user.role = UserRole(role) if role == 'admin' else UserRole.USER
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get_by_id(user_id: int) -> User:
        """Получить пользователя по ID."""
        return User.query.get(user_id)

    @staticmethod
    def get_by_username(username: str) -> User:
        """Получить пользователя по имени."""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_by_email(email: str) -> User:
        """Получить пользователя по email."""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_all() -> list:
        """Получить всех пользователей."""
        return User.query.all()

    @staticmethod
    def update(user: User, **kwargs) -> User:
        """Обновить данные пользователя."""
        from app.models.user import UserRole
        for key, value in kwargs.items():
            if key == 'role':
                try:
                    user.role = UserRole(value)
                except ValueError:
                    pass
            elif key != 'password_hash' and hasattr(user, key):
                setattr(user, key, value)
        db.session.commit()
        return user

    @staticmethod
    def delete(user: User) -> bool:
        """Удалить пользователя."""
        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def verify_password(user: User, password: str) -> bool:
        """Проверить пароль пользователя."""
        return check_password_hash(user.password_hash, password)