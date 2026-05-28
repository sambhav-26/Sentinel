"""Initial schema creation

Revision ID: 001_initial
Revises:
Create Date: 2026-05-28 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('api_key', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.UniqueConstraint('api_key', name='uq_users_api_key'),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create repositories table
    op.create_table(
        'repositories',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('url', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_user_repo_name'),
    )

    # Create scans table
    op.create_table(
        'scans',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('repository_id', sa.String(36), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='queued'),
        sa.Column('progress', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_files', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('files_scanned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['repository_id'], ['repositories.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_scans_status', 'scans', ['status'])

    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('scan_id', sa.String(36), nullable=False),
        sa.Column('vulnerability_type', sa.String(255), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('line_number', sa.Integer(), nullable=False),
        sa.Column('column_number', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cwe_id', sa.String(20), nullable=True),
        sa.Column('cwe_name', sa.String(255), nullable=True),
        sa.Column('owasp_category', sa.String(255), nullable=True),
        sa.Column('exploitability_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('code_snippet', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('recommendation', sa.Text(), nullable=True),
        sa.Column('is_ignored', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('ignore_reason', sa.Text(), nullable=True),
        sa.Column('detection_source', sa.String(100), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create attacks table
    op.create_table(
        'attacks',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('scan_id', sa.String(36), nullable=False),
        sa.Column('finding_id', sa.String(36), nullable=True),
        sa.Column('attack_type', sa.String(255), nullable=False),
        sa.Column('attack_vector', sa.String(255), nullable=True),
        sa.Column('success_probability', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('impact_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('mitre_technique', sa.String(20), nullable=True),
        sa.Column('mitre_tactic', sa.String(100), nullable=True),
        sa.Column('attack_path', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('impact_description', sa.Text(), nullable=True),
        sa.Column('prerequisites', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('mitigation', sa.Text(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.ForeignKeyConstraint(['finding_id'], ['findings.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create patches table
    op.create_table(
        'patches',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('scan_id', sa.String(36), nullable=False),
        sa.Column('finding_id', sa.String(36), nullable=True),
        sa.Column('original_code', sa.Text(), nullable=False),
        sa.Column('patched_code', sa.Text(), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('additional_context', sa.Text(), nullable=True),
        sa.Column('is_ai_generated', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('can_auto_apply', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('apply_complexity', sa.String(50), nullable=True),
        sa.Column('applied', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('applied_at', sa.DateTime(), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.ForeignKeyConstraint(['finding_id'], ['findings.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create reports table
    op.create_table(
        'reports',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('scan_id', sa.String(36), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('overall_risk_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('critical_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('high_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('medium_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('low_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('patch_coverage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('remediation_effort', sa.String(50), nullable=True),
        sa.Column('estimated_remediation_time', sa.Integer(), nullable=True),
        sa.Column('pdf_url', sa.String(500), nullable=True),
        sa.Column('json_data', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('executive_summary', sa.Text(), nullable=True),
        sa.Column('detailed_findings', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('recommendations', sa.JSON(), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create agent_logs table
    op.create_table(
        'agent_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('scan_id', sa.String(36), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('agent_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('log_level', sa.String(20), nullable=False, server_default='INFO'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('execution_time_ms', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['scan_id'], ['scans.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table('agent_logs')
    op.drop_table('reports')
    op.drop_table('patches')
    op.drop_table('attacks')
    op.drop_table('findings')
    op.drop_table('scans')
    op.drop_table('repositories')
    op.drop_table('users')
