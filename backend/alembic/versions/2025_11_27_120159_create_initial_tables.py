"""
create_initial_tables

Initial migration to create all base tables for Viral Clip AI
Similar to Laravel's create_xxx_table migrations

Revision ID: 037fd98aee2b
Revises: 
Create Date: 2025-11-27 12:01:59.740086
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '037fd98aee2b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create all initial tables
    Similar to: php artisan migrate
    """
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='created'),
        sa.Column('source_language', sa.String(), server_default='en'),
        sa.Column('target_platform', sa.String(), server_default='shorts'),
        sa.Column('target_duration', sa.Integer(), server_default='60'),
        sa.Column('aspect_ratio', sa.String(), server_default='9:16'),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('original_filename', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('fps', sa.Float(), nullable=True),
        sa.Column('codec', sa.String(), nullable=True),
        sa.Column('bitrate', sa.Integer(), nullable=True),
        sa.Column('source_type', sa.String(), server_default='upload'),
        sa.Column('source_url', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='uploaded'),
        sa.Column('processing_progress', sa.Integer(), server_default='0'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('audio_path', sa.String(), nullable=True),
        sa.Column('thumbnail_path', sa.String(), nullable=True),
        sa.Column('transcription_path', sa.String(), nullable=True),
        sa.Column('has_transcription', sa.Boolean(), server_default='0'),
        sa.Column('transcript', sa.JSON(), nullable=True),
        sa.Column('scenes', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create clips table
    op.create_table(
        'clips',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('projects.id'), nullable=False),
        sa.Column('video_id', sa.Integer(), sa.ForeignKey('videos.id'), nullable=False),  # REQUIRED
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('duration', sa.Float(), nullable=False),
        sa.Column('viral_score', sa.Float(), server_default='0.0'),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('aspect_ratio', sa.String(), server_default='9:16'),
        sa.Column('resolution', sa.String(), server_default='1080p'),
        sa.Column('fps', sa.Integer(), server_default='30'),
        sa.Column('subtitle_style', sa.JSON(), nullable=True),
        sa.Column('overlays', sa.JSON(), nullable=True),
        sa.Column('audio_settings', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(), server_default='detected'),
        sa.Column('exported', sa.Boolean(), server_default='0'),
        sa.Column('export_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create subtitles table
    op.create_table(
        'subtitles',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('video_id', sa.Integer(), sa.ForeignKey('videos.id'), nullable=True),
        sa.Column('clip_id', sa.Integer(), sa.ForeignKey('clips.id'), nullable=True),
        sa.Column('text', sa.String(), nullable=False),
        sa.Column('start_time', sa.Float(), nullable=False),
        sa.Column('end_time', sa.Float(), nullable=False),
        sa.Column('style', sa.JSON(), nullable=True),
        sa.Column('language', sa.String(), server_default='en'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )
    
    # Create indexes for better query performance
    op.create_index('ix_videos_project_id', 'videos', ['project_id'])
    op.create_index('ix_clips_project_id', 'clips', ['project_id'])
    op.create_index('ix_clips_video_id', 'clips', ['video_id'])
    op.create_index('ix_subtitles_video_id', 'subtitles', ['video_id'])
    op.create_index('ix_subtitles_clip_id', 'subtitles', ['clip_id'])


def downgrade() -> None:
    """
    Drop all tables (rollback)
    Similar to: php artisan migrate:rollback
    """
    # Drop indexes first
    op.drop_index('ix_subtitles_clip_id', 'subtitles')
    op.drop_index('ix_subtitles_video_id', 'subtitles')
    op.drop_index('ix_clips_video_id', 'clips')
    op.drop_index('ix_clips_project_id', 'clips')
    op.drop_index('ix_videos_project_id', 'videos')
    
    # Drop tables in reverse order (respect foreign keys)
    op.drop_table('subtitles')
    op.drop_table('clips')
    op.drop_table('videos')
    op.drop_table('projects')
