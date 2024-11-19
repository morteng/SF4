"""Broken migration description

Revision ID: broken_revision_id
Revises: some_revision_id
Create Date: 2024-11-19 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# Remove the problematic line
# from handlers import some_handler

# revision identifiers, used by Alembic.
revision = 'broken_revision_id'
down_revision = 'some_revision_id'
branch_labels = None
depends_on = None

def upgrade():
    # Example upgrade operation
    op.create_table(
        'example_table',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(50), nullable=False)
    )

def downgrade():
    # Example downgrade operation
    op.drop_table('example_table')
