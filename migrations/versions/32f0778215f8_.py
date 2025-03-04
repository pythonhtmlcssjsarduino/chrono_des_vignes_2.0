"""empty message

Revision ID: 32f0778215f8
Revises: b97b5e6296ac
Create Date: 2024-12-18 17:21:50.998272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32f0778215f8'
down_revision = 'b97b5e6296ac'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('edition', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=False))

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.Text(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.drop_column('description')

    with op.batch_alter_table('edition', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
