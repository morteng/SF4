from app.extensions import db

stipend_tag_association = db.Table(
    'stipend_tag_association',
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

organization_stipends = db.Table(
    'organization_stipends',
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
    db.Column('stipend_id', db.Integer, db.ForeignKey('stipend.id'), primary_key=True)
)

# Define the association table between User and Organization
user_organization = db.Table(
    'user_organization',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True)
)

# Define the association table between Bot and Tag
bot_tag = db.Table(
    'bot_tag',
    db.Column('bot_id', db.Integer, db.ForeignKey('bot.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)
