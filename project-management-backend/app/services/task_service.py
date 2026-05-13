from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository


class TaskService:
    """
    Сервис для работы с задачами.
    Содержит бизнес-логику связанную с задачами и подзадачами.
    """

    @staticmethod
    def create_task(title: str, description: str, project_id: int,
                   assignee_id: int = None, status: str = 'todo',
                   parent_id: int = None) -> tuple:
        """
        Создать новую задачу или подзадачу.
        Args:
            title: название задачи
            description: описание задачи
            project_id: ID проекта
            assignee_id: ID исполнителя (опционально)
            status: статус задачи
            parent_id: ID родительской задачи (для подзадач)
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        if not title or not title.strip():
            return False, {'error': 'Task title is required'}, 400

        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return False, {'error': 'Project not found'}, 404

        if parent_id:
            parent_task = TaskRepository.get_by_id(parent_id)
            if not parent_task or parent_task.project_id != project_id:
                return False, {'error': 'Parent task not found in this project'}, 404

        if assignee_id:
            assignee = UserRepository.get_by_id(assignee_id)
            if not assignee:
                return False, {'error': 'Assignee not found'}, 404

        task = TaskRepository.create(
            title=title.strip(),
            description=description,
            project_id=project_id,
            assignee_id=assignee_id,
            status=status,
            parent_id=parent_id
        )
        return True, task, 201

    @staticmethod
    def get_task(task_id: int) -> tuple:
        """Получить задачу по ID."""
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return False, {'error': 'Task not found'}, 404
        return True, task, 200

    @staticmethod
    def get_project_tasks(project_id: int, user_id: int) -> tuple:
        """
        Получить все задачи проекта с подзадачами.
        Args:
            project_id: ID проекта
            user_id: ID пользователя (для проверки доступа)
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        from app.models.user import UserRole, User
        user = UserRepository.get_by_id(user_id)

        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return False, {'error': 'Project not found'}, 404

        if project.owner_id != user_id and user.role != UserRole.ADMIN:
            return False, {'error': 'Access denied'}, 403

        tasks = TaskRepository.get_by_project(project_id)
        tasks_data = []

        for task in tasks:
            task_dict = TaskService._task_to_dict(task)
            task_dict['subtasks'] = [
                TaskService._task_to_dict(st) for st in TaskRepository.get_subtasks(task.id)
            ]
            tasks_data.append(task_dict)

        return True, tasks_data, 200

    @staticmethod
    def _task_to_dict(task):
        """Преобразовать задачу в словарь."""
        return {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'status': task.status.value,
            'project_id': task.project_id,
            'assignee_id': task.assignee_id,
            'assignee_username': task.assignee.username if task.assignee else None,
            'parent_id': task.parent_id,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'updated_at': task.updated_at.isoformat() if task.updated_at else None
        }

    @staticmethod
    def update_task(task_id: int, user_id: int, **kwargs) -> tuple:
        """Обновить задачу."""
        from app.models.user import UserRole, User
        user = UserRepository.get_by_id(user_id)

        task = TaskRepository.get_by_id(task_id)
        if not task:
            return False, {'error': 'Task not found'}, 404

        project = ProjectRepository.get_by_id(task.project_id)
        if project.owner_id != user_id and user.role != UserRole.ADMIN:
            return False, {'error': 'Access denied'}, 403

        task = TaskRepository.update(task, **kwargs)
        return True, TaskService._task_to_dict(task), 200

    @staticmethod
    def delete_task(task_id: int, user_id: int) -> tuple:
        """Удалить задачу и все подзадачи."""
        from app.models.user import UserRole, User
        user = UserRepository.get_by_id(user_id)

        task = TaskRepository.get_by_id(task_id)
        if not task:
            return False, {'error': 'Task not found'}, 404

        project = ProjectRepository.get_by_id(task.project_id)
        if project.owner_id != user_id and user.role != UserRole.ADMIN:
            return False, {'error': 'Access denied'}, 403

        TaskRepository.delete(task)
        return True, {'message': 'Task deleted successfully'}, 200