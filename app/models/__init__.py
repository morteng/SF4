from .association_tables import stipend_tag_association, organization_stipends

def init_models(app):
    from .bot import Bot
    from .notification import Notification
    from .stipend import Stipend
    from .tag import Tag
    from .user import User
    from .organization import Organization
