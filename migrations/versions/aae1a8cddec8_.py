"""empty message

Revision ID: aae1a8cddec8
Revises: 8582d29e22fc
Create Date: 2024-03-30 17:04:45.457074

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aae1a8cddec8'
down_revision: Union[str, None] = '8582d29e22fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
