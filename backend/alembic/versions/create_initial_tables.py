"""Create initial tables

Revision ID: create_initial_tables
Revises: 
Create Date: 2025-09-15 21:37:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_initial_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create job_pages_raw table
    op.create_table('job_pages_raw',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('raw_html', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    
    # Create job_pages_parsed table with all fields including salary normalization
    op.create_table('job_pages_parsed',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_page_raw_id', sa.Integer(), nullable=False),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('employer', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('date_posted', sa.String(), nullable=True),
        sa.Column('primary_salary_min', sa.Float(), nullable=True),
        sa.Column('primary_salary_max', sa.Float(), nullable=True),
        sa.Column('primary_salary_rate', sa.Enum('hourly', 'weekly', 'monthly', 'yearly', 'other', name='salary_rate_enum'), nullable=True),
        sa.Column('secondary_salary_min', sa.Float(), nullable=True),
        sa.Column('secondary_salary_max', sa.Float(), nullable=True),
        sa.Column('secondary_salary_rate', sa.Enum('hourly', 'weekly', 'monthly', 'yearly', 'other', name='salary_rate_enum'), nullable=True),
        sa.Column('job_type', sa.String(), nullable=True),
        sa.Column('skills', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('seniority', sa.String(), nullable=True),
        sa.Column('education_level', sa.String(), nullable=True),
        sa.Column('normalized_salary_min', sa.Float(), nullable=True),
        sa.Column('normalized_salary_max', sa.Float(), nullable=True),
        sa.Column('is_salary_normalizable', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['job_page_raw_id'], ['job_pages_raw.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_page_raw_id')
    )


def downgrade():
    op.drop_table('job_pages_parsed')
    op.drop_table('job_pages_raw')
