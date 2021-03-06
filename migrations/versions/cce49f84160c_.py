"""empty message

Revision ID: cce49f84160c
Revises: 06ba8d7b6bb8
Create Date: 2019-12-22 15:14:40.003045

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cce49f84160c'
down_revision = '06ba8d7b6bb8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('productphoto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('photo_link', sa.String(length=256), nullable=True),
    sa.Column('photo_status', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('productphoto')
    # ### end Alembic commands ###
