"""db improvements

Revision ID: 002
down_revision: 001
Create Date: 2024-01-01 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade() -> None:
    # Add new columns
    op.add_column('resume_versions', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('resume_versions', sa.Column('file_original_name', sa.String(), nullable=True))
    op.add_column('resume_versions', sa.Column('file_size', sa.Integer(), nullable=True))
    op.add_column('resume_versions', sa.Column('file_mime_type', sa.String(), nullable=True))
    op.add_column('resume_versions', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))

    # Create indexes
    op.create_index('ix_resume_versions_user_id', 'resume_versions', ['user_id'])
    op.create_index('ix_resume_versions_created_at', 'resume_versions', ['created_at'])

    # Add unique constraint for (user_id, version_name)
    op.create_unique_constraint('uq_user_version_name', 'resume_versions', ['user_id', 'version_name'])

def downgrade() -> None:
    op.drop_constraint('uq_user_version_name', 'resume_versions', type_='unique')
    op.drop_index('ix_resume_versions_user_id', table_name='resume_versions')
    op.drop_index('ix_resume_versions_created_at', table_name='resume_versions')
    op.drop_column('resume_versions', 'updated_at')
    op.drop_column('resume_versions', 'file_original_name')
    op.drop_column('resume_versions', 'file_size')
    op.drop_column('resume_versions', 'file_mime_type')
    op.drop_column('resume_versions', 'is_deleted') 