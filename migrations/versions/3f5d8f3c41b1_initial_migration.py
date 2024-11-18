"""Initial migration

Revision ID: 3f5d8f3c41b1
Revises: 
Create Date: 2024-11-17 17:15:54.067612

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3f5d8f3c41b1'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(150), unique=True, nullable=False),
        sa.Column('email', sa.String(150), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(200), nullable=False),
        sa.Column('auth_token', sa.String(64), unique=True),
        sa.Column('is_admin', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP"))
    )

    # Create bots table
    op.create_table(
        'bots',
        sa.Column('bot_id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(150), nullable=False),
        sa.Column('description', sa.String(255)),
        sa.Column('status', sa.String(50), default='inactive'),
        sa.Column('last_run', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('error_log', sa.Text())
    )

    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('message', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('read_status', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP"))
    )

    # Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(150), unique=True, nullable=False),
        sa.Column('description', sa.String(255), nullable=False),
        sa.Column('homepage_url', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP"))
    )

    # Create stipends table
    op.create_table(
        'stipends',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(150), unique=True, nullable=False),
        sa.Column('summary', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('homepage_url', sa.String(255), nullable=False),
        sa.Column('application_procedure', sa.Text(), nullable=False),
        sa.Column('eligibility_criteria', sa.Text(), nullable=False),
        sa.Column('application_deadline', sa.DateTime(), nullable=False),
        sa.Column('open_for_applications', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP"))
    )

    # Create tags table
    op.create_table(
        'tags',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(150), unique=True, nullable=False),
        sa.Column('category', sa.String(150), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column('updated_at', sa.DateTime(), default=sa.text("CURRENT_TIMESTAMP"), onupdate=sa.text("CURRENT_TIMESTAMP"))
    )

    # Create association tables
    op.create_table(
        'stipend_tags',
        sa.Column('stipend_id', sa.Integer(), sa.ForeignKey('stipends.id'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tags.id'), primary_key=True)
    )

    op.create_table(
        'stipend_organizations',
        sa.Column('stipend_id', sa.Integer(), sa.ForeignKey('stipends.id'), primary_key=True),
        sa.Column('organization_id', sa.Integer(), sa.ForeignKey('organizations.id'), primary_key=True)
    )


def downgrade():
    # Drop association tables
    op.drop_table('stipend_organizations')
    op.drop_table('stipend_tags')

    # Drop main tables
    op.drop_table('tags')
    op.drop_table('stipends')
    op.drop_table('notifications')
    op.drop_table('bots')
    op.drop_table('users')
