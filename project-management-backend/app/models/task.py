from app.extensions import db
from datetime import datetime
import enum


class TaskStatus(enum.Enum):
    """Перечисление статусов задачи."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(db.Model):
    """
    Модель задачи.
    Поля:
        - id: уникальный идентификатор
        - title: название задачи
        - description: описание задачи
        - status: статус задачи (todo/in_progress/done)
        - project_id: ссылка на проект (FK на projects.id)
        - assignee_id: ссылка на исполнителя (FK на users.id)
        - parent_id: ссылка на родительскую задачу (для подзадач)
        - created_at: дата создания
        - updated_at: дата обновления
    Связи:
        - project: связь с проектом (многие-к-одному)
        - assignee: связь с пользователем (многие-к-одному)
        - subtasks: связь с подзадачами (один-ко-многим)
        - parent: связь с родительской задачей (многие-к-одному)
    """
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subtasks = db.relationship('Task', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')

    def to_dict(self):
        """Преобразовать задачу в словарь."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status.value if hasattr(self.status, 'value') else self.status,
            'project_id': self.project_id,
            'assignee_id': self.assignee_id,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }