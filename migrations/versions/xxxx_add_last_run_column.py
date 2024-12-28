"""Add last_run column to Bot table

Revision ID: xxxx
Revises: yyyy
Create Date: 2024-12-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'xxxx'
down_revision = 'yyyy'
branch_labels = None
depends_on = None

def upgrade():
    # Add last_run column to bot table
    op.add_column('bot', sa.Column('last_run', sa.DateTime(), nullable=True))

def downgrade():
    # Remove last_run column from bot table
    op.drop_column('bot', 'last_run')
