from datetime import datetime

class DeadlineValidator:
    def is_valid_deadline(self, deadline):
        if not deadline:
            return False
        if not isinstance(deadline, datetime):
            raise ValueError("Deadline musi być obiektem datetime")
        return deadline >= datetime.utcnow()
