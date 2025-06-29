from app.models import Project, Task

class StatisticsGenerator:
    def task_count_by_status(self, tasks):
        stats = {}
        for task in tasks:
            stats[task.status] = stats.get(task.status, 0) + 1
        return stats

    def generate_global_stats(self):
        all_tasks = Task.query.all()
        all_projects = Project.query.all()

        return {
            'total_tasks': len(all_tasks),
            'total_projects': len(all_projects),
            'status_counts': self.task_count_by_status(all_tasks)
        }