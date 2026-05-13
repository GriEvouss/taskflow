from app.extensions import db
from datetime import datetime


class Project(db.Model):
    """
    Модель проекта.
    Поля:
        - id: уникальный идентификатор
        - name: название проекта
        - description: описание проекта
        - owner_id: ссылка на владельца (FK на users.id)
        - created_at: дата создания
        - updated_at: дата обновления
    Связи:
        - owner: связь с пользователем (многие-к-одному)
        - tasks: связь с задачами (один-ко-многим)
    """
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default='')
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = db.relationship('Task', backref='project', lazy='dynamic', cascade='all, delete-orphan')