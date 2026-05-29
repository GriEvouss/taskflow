from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository


class StatsService:

    @staticmethod
    def get_dashboard_stats(user_id: int) -> dict:
        from app.models.user import UserRole

        user = UserRepository.get_by_id(user_id)
        if not user:
            return {'error': 'User not found'}

        if user.role == UserRole.ADMIN:
            projects = ProjectRepository.get_all()
            tasks = TaskRepository.get_all()
        else:
            projects = ProjectRepository.get_by_owner(user_id)
            tasks = TaskRepository.get_by_user_projects(user_id)

        status_counts = {'todo': 0, 'in_progress': 0, 'done': 0}
        for t in tasks:
            s = t.status.value if hasattr(t.status, 'value') else str(t.status)
            if s in status_counts:
                status_counts[s] += 1

        return {
            'total_projects': len(projects),
            'total_tasks': len(tasks),
            'tasks_by_status': status_counts
        }
