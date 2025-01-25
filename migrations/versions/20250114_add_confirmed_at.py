"""Add confirmed_at column to user table

Revision ID: 20250114_add_confirmed_at
Revises: 
Create Date: 2025-01-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250114_add_confirmed_at'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('confirmed_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_user_confirmed_at'), 'user', ['confirmed_at'], unique=False)
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'confirmed_at')
    # ### end Alembic commands ###
