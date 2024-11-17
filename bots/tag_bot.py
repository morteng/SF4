class TagBot:
    def __init__(self):
        self.name = "TagBot"
        self.description = "Automatically tags stipends based on content."
        self.status = "inactive"  # Change from 'active' to 'inactive'
        
    def run(self):
        """Run the TagBot to process and tag stipends."""
        self.status = "active"
