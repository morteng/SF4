"""Add confirmed_at column to user table

Revision ID: 2025-01-14_add_confirmed_at
Revises: 
Create Date: 2025-01-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '2025-01-14_add_confirmed_at'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('user', sa.Column('confirmed_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('user', 'confirmed_at')
