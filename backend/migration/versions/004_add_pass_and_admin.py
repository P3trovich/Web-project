"""004_add_pass_and_admin"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from argon2 import PasswordHasher

ph = PasswordHasher()
revision: str = '004'
down_revision: Union[str, Sequence[str], None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    users = table('users',
        column('id', sa.Integer),
        column('name', sa.String),
        column('email', sa.String),
        column('is_verified_author', sa.Boolean),
        column('avatar', sa.String),
        column('is_admin', sa.Boolean),
        column('password', sa.String)
    )

    password123_hash = ph.hash('password123')
    admin123_hash = ph.hash('admin123')

    op.execute(
        users.update().
        where(users.c.id == 1).
        values(
            password=password123_hash,
            is_admin=False
        )
    )
    
    op.execute(
        users.update().
        where(users.c.id == 2).
        values(
            password=password123_hash,
            is_admin=False
        )
    )

    op.execute(
        users.update().
        where(users.c.id == 3).
        values(
            password=admin123_hash,
            is_admin=True
        )
    )



def downgrade() -> None:
    users = table('users',
        column('id', sa.Integer),
        column('password', sa.String),
        column('is_admin', sa.Boolean)
    )

    op.execute(
        users.update().
        where(users.c.id == 1).
        values(
            password=None,
            is_admin=None
        )
    )
    
    op.execute(
        users.update().
        where(users.c.id == 2).
        values(
            password=None,
            is_admin=None
        )
    )
    
    op.execute(
        users.update().
        where(users.c.id == 3).
        values(
            password=None,
            is_admin=None
        )
    )
