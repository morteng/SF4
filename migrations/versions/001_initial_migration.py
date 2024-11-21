"""Initial migration.

Revision ID: 001_initial_migration
Revises: 
Create Date: 2023-10-05 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create tables here
    pass

def downgrade():
    # Drop tables here
    pass
