"""Add blacklisted_tokens table

Revision ID: 92fff7ae5003
Revises: dac83da98a13
Create Date: 2021-02-22 16:28:32.672591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92fff7ae5003'
down_revision = 'dac83da98a13'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist_tokens',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('token', sa.String(), nullable=False),
                    sa.Column('blacklisted_at', sa.DateTime(), nullable=False),
                    sa.PrimaryKeyConstraint(
                        'id', name=op.f('pk__blacklist_tokens')),
                    sa.UniqueConstraint('token', name=op.f(
                        'uq__blacklist_tokens__token')),
                    comment='Storage for blacklisted jwt auth tokens'
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blacklist_tokens')
    # ### end Alembic commands ###