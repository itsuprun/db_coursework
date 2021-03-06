"""empty message

Revision ID: 482640b56423
Revises: cce49f84160c
Create Date: 2019-12-27 18:29:34.528374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '482640b56423'
down_revision = 'cce49f84160c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.String(length=140), nullable=True),
    sa.Column('adress', sa.String(length=140), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index(op.f('ix_order_timestamp'), 'order', ['timestamp'], unique=False)
    op.create_table('orderproduct',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orderproduct')
    op.drop_index(op.f('ix_order_timestamp'), table_name='order')
    op.drop_table('order')
    # ### end Alembic commands ###
