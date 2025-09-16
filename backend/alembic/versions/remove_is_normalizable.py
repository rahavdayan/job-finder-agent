"""Remove is_salary_normalizable column

Revision ID: remove_is_normalizable
Revises: create_initial_tables
Create Date: 2025-09-15 22:06:55.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_is_normalizable'
down_revision = 'create_initial_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.drop_column('job_pages_parsed', 'is_salary_normalizable')

def downgrade() -> None:
    op.add_column('job_pages_parsed', sa.Column('is_salary_normalizable', sa.Boolean(), nullable=True, server_default='false'))
