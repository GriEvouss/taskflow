from app.extensions import db
from app.models.task import Task


class TaskRepository:
    """
    Репозиторий для работы с задачами.
    Реализует CRUD операции для модели Task.
    """

    @staticmethod
    def create(title: str, description: str, project_id: int,
               assignee_id: int = None, status: str = 'todo',
               parent_id: int = None) -> Task:
        """
        Создать новую задачу.
        Args:
            title: название задачи
            description: описание задачи
            project_id: ID проекта
            assignee_id: ID исполнителя (опционально)
            status: статус задачи (по умолчанию 'todo')
            parent_id: ID родительской задачи (для подзадач)
        Returns:
            Task: созданный объект задачи
        """
        task = Task(
            title=title,
            description=description,
            project_id=project_id,
            assignee_id=assignee_id,
            parent_id=parent_id
        )
        if status:
            from app.models.task import TaskStatus
            task.status = TaskStatus(status)
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def get_by_id(task_id: int) -> Task:
        """Получить задачу по ID."""
        return Task.query.get(task_id)

    @staticmethod
    def get_by_project(project_id: int) -> list:
        """Получить все задачи проекта (только верхнего уровня)."""
        return Task.query.filter_by(project_id=project_id, parent_id=None).all()

    @staticmethod
    def get_subtasks(parent_id: int) -> list:
        """Получить все подзадачи."""
        return Task.query.filter_by(parent_id=parent_id).all()

    @staticmethod
    def get_by_assignee(assignee_id: int) -> list:
        """Получить все задачи исполнителя."""
        return Task.query.filter_by(assignee_id=assignee_id).all()

    @staticmethod
    def get_all() -> list:
        """Получить все задачи."""
        return Task.query.all()

    @staticmethod
    def update(task: Task, **kwargs) -> Task:
        """Обновить данные задачи."""
        from app.models.task import TaskStatus
        for key, value in kwargs.items():
            if key == 'status' and value:
                try:
                    setattr(task, key, TaskStatus(value))
                except ValueError:
                    pass
            elif hasattr(task, key):
                setattr(task, key, value)
        db.session.commit()
        return task

    @staticmethod
    def delete(task: Task) -> bool:
        """Удалить задачу и все её подзадачи."""
        for subtask in task.subtasks:
            TaskRepository.delete(subtask)
        db.session.delete(task)
        db.session.commit()
        return True