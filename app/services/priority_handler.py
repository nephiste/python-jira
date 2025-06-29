class PriorityHandler:
    def normalize_priority(self, priority_str):
        """Zwraca znormalizowaną wartość priorytetu."""
        normalized = priority_str.strip().lower()
        if normalized in ['wysoki', 'high']:
            return 'High'
        elif normalized in ['średni', 'sredni', 'medium']:
            return 'Medium'
        elif normalized in ['niski', 'low']:
            return 'Low'
        else:
            return 'Medium'  # domyślnie

    def is_valid_priority(self, priority):
        """Sprawdza, czy priorytet należy do dozwolonych."""
        return priority in ['Low', 'Medium', 'High']

    def compare_priority(self, p1, p2):
        """Zwraca -1 jeśli p1 < p2, 0 jeśli równe, 1 jeśli p1 > p2."""
        order = {'Low': 1, 'Medium': 2, 'High': 3}
        return (order[p1] > order[p2]) - (order[p1] < order[p2])
