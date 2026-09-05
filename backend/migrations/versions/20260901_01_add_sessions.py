"""add revocable sessions

Revision ID: 20260901_01
"""
from alembic import op
import sqlalchemy as sa

revision = "20260901_01"
down_revision = "20260901_00"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "sessoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_jti_hash", sa.String(64), nullable=False),
        sa.Column("user_agent", sa.String(300)),
        sa.Column("ip_address", sa.String(64)),
        sa.Column("criada_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("ultima_atividade_em", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expira_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revogada_em", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_sessoes_usuario_id", "sessoes", ["usuario_id"])
    op.create_index("ix_sessoes_refresh_jti_hash", "sessoes", ["refresh_jti_hash"], unique=True)

def downgrade():
    op.drop_index("ix_sessoes_refresh_jti_hash", table_name="sessoes")
    op.drop_index("ix_sessoes_usuario_id", table_name="sessoes")
    op.drop_table("sessoes")
