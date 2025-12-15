"""001_create_tables"""

from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('registration_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_verified_author', sa.Boolean(), nullable=True),
        sa.Column('avatar', sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('news',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('publication_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('cover_image', sa.String(length=200), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table('comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('news_id', sa.Integer(), nullable=True),
        sa.Column('author_id', sa.Integer(), nullable=True),
        sa.Column('publication_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['news_id'], ['news.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    op.drop_table('comments')
    op.drop_table('news')
    op.drop_table('users')