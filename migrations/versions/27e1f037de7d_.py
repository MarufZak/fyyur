"""empty message

Revision ID: 27e1f037de7d
Revises: 
Create Date: 2023-04-14 20:21:49.553071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27e1f037de7d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.add_column(sa.Column('venue_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('artist_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('start_time', sa.DateTime(), nullable=False))
        batch_op.create_foreign_key('venue_id', 'Venue', ['venue_id'], ['id'])
        batch_op.create_foreign_key('artist_id', 'Artist', ['artist_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.drop_constraint('artist_id', type_='foreignkey')
        batch_op.drop_constraint('venue_id', type_='foreignkey')
        batch_op.drop_column('start_time')
        batch_op.drop_column('artist_id')
        batch_op.drop_column('venue_id')

    # ### end Alembic commands ###
