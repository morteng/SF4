from alembic import command
from alembic.config import Config
config = Config('migrations/alembic.ini')
command.upgrade(config, 'head')