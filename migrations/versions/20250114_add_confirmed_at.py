"""Add confirmed_at column to user table

Revision ID: 20250114_add_confirmed_at
Revises: 
Create Date: 2025-01-14

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250114_add_confirmed_at'
down_revision = '20240101_initial'  # Reference previous migration
branch_labels = None
depends_on = None

def upgrade():
    context = op.get_context()
    
    if context.connection.engine.name == 'sqlite':
        with op.batch_alter_table('user') as batch_op:
            batch_op.add_column(sa.Column('confirmed_at', sa.DateTime(), nullable=True))
            batch_op.create_index('ix_user_confirmed_at', ['confirmed_at'], unique=False)
    else:
        op.add_column('user',
            sa.Column('confirmed_at', sa.DateTime(), nullable=True)
        )
        op.create_index(op.f('ix_user_confirmed_at'), 'user', ['confirmed_at'], unique=False)

def downgrade():
    context = op.get_context()
    if context.connection.engine.name == 'sqlite':
        with op.batch_alter_table('user') as batch_op:
            batch_op.drop_index('ix_user_confirmed_at')
            batch_op.drop_column('confirmed_at')
    else:
        op.drop_index(op.f('ix_user_confirmed_at'), table_name='user')
        op.drop_column('user', 'confirmed_at')
