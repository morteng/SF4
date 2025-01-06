from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add stipends relationship to Tag model
    op.create_table(
        'stipend_tags',
        sa.Column('stipend_id', sa.Integer(), sa.ForeignKey('stipend.id'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tag.id'), primary_key=True)
    )

def downgrade():
    op.drop_table('stipend_tags')

if __name__ == "__main__":
    from alembic.config import Config
    from alembic import command
    
    config = Config('migrations/alembic.ini')
    command.upgrade(config, 'head')
