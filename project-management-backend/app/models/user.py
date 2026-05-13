from app.extensions import db
from datetime import datetime
import enum


class UserRole(enum.Enum):
    """Перечисление ролей пользователей."""
    USER = "user"
    ADMIN = "admin"


class User(db.Model):
    """
    Модель пользователя системы.
    Поля:
        - id: уникальный идентификатор
        - username: уникальное имя пользователя
        - email: уникальный email
        - password_hash: хеш пароля
        - role: роль пользователя (user/admin)
        - created_at: дата создания
    Связи:
        - projects: связь с проектами (один-ко-многим)
        - tasks: связь с задачами (один-ко-многим)
    """
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    projects = db.relationship('Project', backref='owner', lazy='dynamic')
    tasks = db.relationship('Task', backref='assignee', lazy='dynamic')

    def to_dict(self):
        """Преобразовать пользователя в словарь."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value if hasattr(self.role, 'value') else 'user',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }