"""add unique constraint on roles table (one project - one user role)

Revision ID: 83ac0424087f
Revises: ef6d484b3d39
Create Date: 2021-04-15 14:53:39.086815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83ac0424087f'
down_revision = 'ef6d484b3d39'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(op.f('uq__roles__user_id_project_id'), 'roles', ['user_id', 'project_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq__roles__user_id_project_id'), 'roles', type_='unique')
    # ### end Alembic commands ###