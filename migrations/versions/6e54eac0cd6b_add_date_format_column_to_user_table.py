"""Add date_format column to user table

Revision ID: 6e54eac0cd6b
Revises: 26dd3a7081ec
Create Date: 2025-05-04 13:28:03.743117

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e54eac0cd6b'
down_revision = '26dd3a7081ec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date_format', sa.String(length=20), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('date_format')

    # ### end Alembic commands ###
