import logging

class TagBot:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tags = {
            'scholarship': ['scholarship', 'grant'],
            'internship': ['internship', 'work experience'],
            'fellowship': ['fellowship', 'research']
        }

    def tag_stipend(self, stipend_content):
        """
        Tags a stipend based on the content provided.

        :param stipend_content: str - The content of the stipend to be tagged.
        :return: list - A list of tags for the stipend.
        """
        stipend_content_lower = stipend_content.lower()
        matched_tags = []

        for tag, keywords in self.tags.items():
            if any(keyword in stipend_content_lower for keyword in keywords):
                matched_tags.append(tag)

        self.logger.info(f"Tagged stipend with: {matched_tags}")
        return matched_tags
