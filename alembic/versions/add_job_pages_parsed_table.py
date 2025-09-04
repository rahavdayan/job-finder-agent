"""Add job_pages_parsed table

Revision ID: add_job_pages_parsed_table
Revises: 001_initial_migration
Create Date: 2025-09-03 21:25:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_job_pages_parsed_table'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Create the job_pages_parsed table
    op.create_table(
        'job_pages_parsed',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True, index=True),
        sa.Column('job_page_raw_id', sa.Integer(), sa.ForeignKey('job_pages_raw.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('job_title', sa.String(), nullable=True),
        sa.Column('employer', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('date_posted', sa.String(), nullable=True),
        sa.Column('salary', sa.String(), nullable=True),
        sa.Column('job_type', sa.String(), nullable=True),
        sa.Column('skills', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('seniority', sa.String(), nullable=True),
        sa.Column('education_level', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    
    # Create an index on the foreign key for better join performance
    op.create_index(op.f('ix_job_pages_parsed_job_page_raw_id'), 'job_pages_parsed', ['job_page_raw_id'], unique=True)

def downgrade():
    # Drop the index first
    op.drop_index(op.f('ix_job_pages_parsed_job_page_raw_id'), table_name='job_pages_parsed')
    
    # Then drop the table
    op.drop_table('job_pages_parsed')
