"""Personal Detail

Revision ID: 4b64f15cc25f
Revises: f1a9963bdace
Create Date: 2023-07-29 10:08:55.710363

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b64f15cc25f'
down_revision = 'f1a9963bdace'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        
    )


def downgrade() -> None:
    pass
