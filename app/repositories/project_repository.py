from app.extensions import db
from app.models.project import Project


class ProjectRepository:
    """
    Репозиторий для работы с проектами.
    Реализует CRUD операции для модели Project.
    """

    @staticmethod
    def create(name: str, description: str, owner_id: int) -> Project:
        """
        Создать новый проект.
        Args:
            name: название проекта
            description: описание проекта
            owner_id: ID владельца проекта
        Returns:
            Project: созданный объект проекта
        """
        project = Project(name=name, description=description, owner_id=owner_id)
        db.session.add(project)
        db.session.commit()
        return project

    @staticmethod
    def get_by_id(project_id: int) -> Project:
        """Получить проект по ID."""
        return Project.query.get(project_id)

    @staticmethod
    def get_by_owner(owner_id: int) -> list:
        """Получить все проекты владельца."""
        return Project.query.filter_by(owner_id=owner_id).all()

    @staticmethod
    def get_all() -> list:
        """Получить все проекты."""
        return Project.query.all()

    @staticmethod
    def update(project: Project, **kwargs) -> Project:
        """Обновить данные проекта."""
        for key, value in kwargs.items():
            if hasattr(project, key):
                setattr(project, key, value)
        db.session.commit()
        return project

    @staticmethod
    def delete(project: Project) -> bool:
        """Удалить проект."""
        db.session.delete(project)
        db.session.commit()
        return True