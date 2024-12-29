class BaseService:
    def __init__(self):
        self._create_limit = None  # Initialize the private attribute

    @property
    def create_limit(self):
        """Getter for create_limit."""
        return self._create_limit

    @create_limit.setter
    def create_limit(self, value):
        """Setter for create_limit."""
        self._create_limit = value
