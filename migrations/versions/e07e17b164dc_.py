"""empty message

Revision ID: e07e17b164dc
Revises: 3178c237522d
Create Date: 2025-05-05 17:59:41.773847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e07e17b164dc'
down_revision = '3178c237522d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('preferred_currency', sa.String(length=10), nullable=True))
        batch_op.drop_column('dark_mode')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user_settings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('dark_mode', sa.BOOLEAN(), nullable=True))
        batch_op.drop_column('preferred_currency')

    # ### end Alembic commands ###
