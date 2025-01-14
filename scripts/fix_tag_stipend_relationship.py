from alembic import op
import sqlalchemy as sa
from app.extensions import db

def upgrade():
    # Create tag table first
    op.create_table(
        'tag',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('category', sa.String(100)),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Add JSONB column to stipend table
    op.add_column('stipend', 
        sa.Column('tags', sa.JSON(none_as_null=True), nullable=True)
    )
    
    # Create many-to-many relationship table
    op.create_table(
        'stipend_tags',
        sa.Column('stipend_id', sa.Integer(), sa.ForeignKey('stipend.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('tag_id', sa.Integer(), sa.ForeignKey('tag.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now())
    )

def downgrade():
    op.drop_table('stipend_tags')
    op.drop_column('stipend', 'tags')
    op.drop_table('tag')

if __name__ == "__main__":
    from alembic.config import Config
    from alembic import command
    
    # Configure and run migration
    config = Config('migrations/alembic.ini')
    command.upgrade(config, 'head')
    
    # Verify schema
    from app.models import Tag
    db.create_all()
    print("Schema migration completed successfully")
