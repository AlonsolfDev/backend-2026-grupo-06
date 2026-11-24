"""Autenticación, refresh tokens y recuperación de contraseña

Revision ID: a1b2c3d4e5f6
Revises: e4571a0ef542
Create Date: 2026-11-22 12:00:00.000000

Agrega:
- Columnas de credenciales en `usuarios` (hash Argon2id, intentos, bloqueo).
- Tabla `refresh_tokens` (solo se guarda el hash SHA-256 del token opaco).
- Tabla `recuperacion_tokens` (registro del `jti` para garantizar uso único).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e4571a0ef542"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Credenciales del usuario -----------------------------------------
    op.add_column(
        "usuarios",
        sa.Column("password_hash", sa.String(length=255), nullable=False, server_default=""),
    )
    op.add_column(
        "usuarios",
        sa.Column("intentos_fallidos", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column("usuarios", sa.Column("bloqueado_hasta", sa.DateTime(), nullable=True))
    op.create_index("ix_usuarios_correo", "usuarios", ["correo"], unique=False)

    # --- Refresh tokens (opacos, guardados como hash) ----------------------
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expira_en", sa.DateTime(), nullable=False),
        sa.Column("revocado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_refresh_tokens_usuario_id", "refresh_tokens", ["usuario_id"])
    op.create_index("ix_refresh_tokens_token_hash", "refresh_tokens", ["token_hash"])

    # --- Tokens de recuperación (jti de un solo uso) ----------------------
    op.create_table(
        "recuperacion_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False),
        sa.Column("expira_en", sa.DateTime(), nullable=False),
        sa.Column("usado", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("jti"),
    )
    op.create_index("ix_recuperacion_tokens_usuario_id", "recuperacion_tokens", ["usuario_id"])
    op.create_index("ix_recuperacion_tokens_jti", "recuperacion_tokens", ["jti"])


def downgrade() -> None:
    op.drop_index("ix_recuperacion_tokens_jti", table_name="recuperacion_tokens")
    op.drop_index("ix_recuperacion_tokens_usuario_id", table_name="recuperacion_tokens")
    op.drop_table("recuperacion_tokens")

    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_usuario_id", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    op.drop_index("ix_usuarios_correo", table_name="usuarios")
    op.drop_column("usuarios", "bloqueado_hasta")
    op.drop_column("usuarios", "intentos_fallidos")
    op.drop_column("usuarios", "password_hash")
