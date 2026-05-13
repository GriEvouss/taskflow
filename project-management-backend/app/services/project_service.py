from app.repositories.project_repository import ProjectRepository


class ProjectService:
    """
    Сервис для работы с проектами.
    Содержит бизнес-логику связанную с проектами.
    """

    @staticmethod
    def create_project(name: str, description: str, owner_id: int) -> tuple:
        """
        Создать новый проект.
        Args:
            name: название проекта
            description: описание проекта
            owner_id: ID владельца
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        if not name or not name.strip():
            return False, {'error': 'Project name is required'}, 400

        project = ProjectRepository.create(name.strip(), description, owner_id)
        return True, project, 201

    @staticmethod
    def get_project(project_id: int, user_id: int) -> tuple:
        """
        Получить проект по ID.
        Args:
            project_id: ID проекта
            user_id: ID пользователя (для проверки доступа)
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return False, {'error': 'Project not found'}, 404

        if project.owner_id != user_id:
            return False, {'error': 'Access denied'}, 403

        return True, project, 200

    @staticmethod
    def get_user_projects(user_id: int) -> tuple:
        """
        Получить все проекты пользователя.
        Args:
            user_id: ID пользователя
        Returns:
            tuple: (успех, данные, код статуса)
        """
        projects = ProjectRepository.get_by_owner(user_id)
        return True, projects, 200

    @staticmethod
    def update_project(project_id: int, user_id: int, **kwargs) -> tuple:
        """
        Обновить проект.
        Args:
            project_id: ID проекта
            user_id: ID пользователя (для проверки доступа)
            **kwargs: поля для обновления
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return False, {'error': 'Project not found'}, 404

        if project.owner_id != user_id:
            return False, {'error': 'Access denied'}, 403

        project = ProjectRepository.update(project, **kwargs)
        return True, project, 200

    @staticmethod
    def delete_project(project_id: int, user_id: int) -> tuple:
        """
        Удалить проект.
        Args:
            project_id: ID проекта
            user_id: ID пользователя (для проверки доступа)
        Returns:
            tuple: (успех, данные или сообщение об ошибке, код статуса)
        """
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return False, {'error': 'Project not found'}, 404

        if project.owner_id != user_id:
            return False, {'error': 'Access denied'}, 403

        ProjectRepository.delete(project)
        return True, {'message': 'Project deleted successfully'}, 200