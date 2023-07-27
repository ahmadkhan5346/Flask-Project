"""Employee table create

Revision ID: f1a9963bdace
Revises: 
Create Date: 2023-07-27 17:41:19.798327

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1a9963bdace'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "employee",
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('phone', sa.String(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('employee')
