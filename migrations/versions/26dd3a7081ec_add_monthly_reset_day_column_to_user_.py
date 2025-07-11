"""Add monthly_reset_day column to user table

Revision ID: 26dd3a7081ec
Revises: f6071d3bd89f
Create Date: 2025-05-04 13:12:00.100737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '26dd3a7081ec'
down_revision = 'f6071d3bd89f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('monthly_reset_day', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('weekly_reset_day', sa.String(length=10), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('weekly_reset_day')
        batch_op.drop_column('monthly_reset_day')

    # ### end Alembic commands ###
