"""baseline user schema

Revision ID: 20260901_00
"""
from alembic import op
import sqlalchemy as sa

revision = "20260901_00"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("email", sa.String(120), nullable=False),
        sa.Column("senha_hash", sa.String(255), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("email_verificado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("criado_em", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("ultimo_login", sa.DateTime(timezone=True)),
        sa.Column("reset_token_hash", sa.String(255)),
        sa.Column("reset_token_expira_em", sa.DateTime(timezone=True)),
        sa.Column("verificacao_token_hash", sa.String(255)),
        sa.Column("verificacao_token_expira_em", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_usuarios_id", "usuarios", ["id"])
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)

def downgrade():
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_index("ix_usuarios_id", table_name="usuarios")
    op.drop_table("usuarios")
