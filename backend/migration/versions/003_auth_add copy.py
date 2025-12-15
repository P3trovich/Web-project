"""003_auth_add

Revision ID: e650850fb303
Revises: 002
Create Date: 2025-10-15 15:02:03.241354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '003'
down_revision: Union[str, Sequence[str], None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('refresh_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('refresh_token', sa.String(length=500), nullable=False),
    sa.Column('user_agent', sa.Text(), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_refresh_sessions_id'), 'refresh_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_refresh_sessions_refresh_token'), 'refresh_sessions', ['refresh_token'], unique=True)
    op.create_index(op.f('ix_comments_id'), 'comments', ['id'], unique=False)
    op.create_index(op.f('ix_news_id'), 'news', ['id'], unique=False)
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('password', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('github_id', sa.String, nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'github_id')
    op.drop_column('users', 'password')
    op.drop_column('users', 'is_admin')
    op.drop_index(op.f('ix_news_id'), table_name='news')
    op.drop_index(op.f('ix_comments_id'), table_name='comments')
    op.drop_index(op.f('ix_refresh_sessions_refresh_token'), table_name='refresh_sessions')
    op.drop_index(op.f('ix_refresh_sessions_id'), table_name='refresh_sessions')
    op.drop_table('refresh_sessions')
