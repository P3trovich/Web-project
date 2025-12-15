"""005_add_admin"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from argon2 import PasswordHasher

ph = PasswordHasher()
revision: str = '005'
down_revision: Union[str, Sequence[str], None] = '004'
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

    admin123_hash = ph.hash('admin123')

    op.bulk_insert(users, [
        {
            #'id': 1, # Добавлено вручную
            'name': 'Админ',
            'email': 'admin@example.com',
            'is_verified_author': True,
            'is_admin': True,
            'avatar': '1.png',
            'password': admin123_hash
        },
    ])

    op.execute(
        users.update().
        where(users.c.id == 3).
        values(
            password=admin123_hash,
        )
    )

def downgrade() -> None:
    users = table('users',
        column('id', sa.Integer),
        column('name', sa.String),
        column('email', sa.String),
        column('is_verified_author', sa.Boolean),
        column('avatar', sa.String),
        column('is_admin', sa.Boolean),
        column('password', sa.String)
    )
    
    # Удаляем пользователя с email 'admin@example.com'
    op.execute(
        users.delete().
        where(users.c.email == 'admin@example.com')
    )