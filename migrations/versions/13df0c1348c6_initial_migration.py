"""Initial migration.

Revision ID: 13df0c1348c6
Revises: 3f5d8f3c41b1
Create Date: 2024-11-18 11:29:20.584562

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '13df0c1348c6'
down_revision: Union[str, None] = '3f5d8f3c41b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
