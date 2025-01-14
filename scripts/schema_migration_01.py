from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

def upgrade():
    # Add new JSONB column
    op.add_column('stipend', 
        sa.Column('tags_new', JSONB(none_as_null=True), nullable=True)
    )
    
    # Copy data from old column to new column
    op.execute("""
        UPDATE stipend 
        SET tags_new = jsonb_build_array(tags::text)
        WHERE tags IS NOT NULL
    """)
    
    # Drop old column
    op.drop_column('stipend', 'tags')
    
    # Rename new column
    op.alter_column('stipend', 'tags_new', new_column_name='tags')

def downgrade():
    # Add back old NUMERIC column
    op.add_column('stipend',
        sa.Column('tags_old', sa.NUMERIC(), nullable=True)
    )
    
    # Copy data back to old column
    op.execute("""
        UPDATE stipend
        SET tags_old = (tags->>0)::numeric
        WHERE jsonb_array_length(tags) > 0
    """)
    
    # Drop JSONB column
    op.drop_column('stipend', 'tags')
    
    # Rename old column
    op.alter_column('stipend', 'tags_old', new_column_name='tags')
