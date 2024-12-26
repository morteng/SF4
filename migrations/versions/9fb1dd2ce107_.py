"""empty message

Revision ID: 9fb1dd2ce107
Revises: 
Create Date: 2024-05-08 15:17:17.999777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fb1dd2ce107'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('stipend', schema=None) as batch_op:
        batch_op.add_column(sa.Column('organization_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_stipend_organization_id', 'organization', ['organization_id'], ['id'])


def downgrade():
    with op.batch_alter_table('stipend', schema=None) as batch_op:
        batch_op.drop_constraint('fk_stipend_organization_id', type_='foreignkey')
        batch_op.drop_column('organization_id')
