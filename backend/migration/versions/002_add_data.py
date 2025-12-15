"""002_add_data"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

revision = '002'
down_revision = '001'

def upgrade() -> None:
    users = table('users',
        #column('id', sa.Integer), # Добавлено вручную
        column('name', sa.String),
        column('email', sa.String),
        column('is_verified_author', sa.Boolean),
        column('avatar', sa.String)
    )
    
    news = table('news',
        #column('id', sa.Integer), # Добавлено вручную
        column('title', sa.String),
        column('content', sa.Text),
        column('author_id', sa.Integer),
        column('cover_image', sa.String)
    )
    
    comments = table('comments',
        column('text', sa.Text),
        column('news_id', sa.Integer),
        column('author_id', sa.Integer)
    )
    
    # Вставляем данные и получаем ID
    op.bulk_insert(users, [
        {
            #'id': 1, # Добавлено вручную
            'name': 'Иван Иванов',
            'email': 'ivan@example.com',
            'is_verified_author': True,
            'avatar': '1.png'
        },
        {
            #'id': 2, # Добавлено вручную
            'name': 'Петр Петров',
            'email': 'petr@example.com',
            'is_verified_author': False,
            'avatar': '2.png'
        }
    ])
    
    # Для news нужен author_id, предполагаем что первый пользователь имеет id=1
    op.bulk_insert(news, [
        {
            #'id': 1, # Добавлено вручную
            'title': 'Первая новость',
            'content': 'Содержание первой новости',
            'author_id': 1,
            'cover_image': 'cover.png'
        }
    ])
    
    op.bulk_insert(comments, [
        {
            'text': 'Отличная новость!',
            'news_id': 1,
            'author_id': 2
        }
    ])

def downgrade() -> None:
    op.execute("DELETE FROM comments")
    op.execute("DELETE FROM news")
    op.execute("DELETE FROM users")