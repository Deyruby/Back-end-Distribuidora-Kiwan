"""empty message

Revision ID: 5795efdb435b
Revises: 
Create Date: 2024-10-08 11:19:19.362287

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5795efdb435b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('image', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('offer_carrusel', sa.Boolean(), nullable=True),
    sa.Column('price', sa.String(), nullable=True),
    sa.Column('offer', sa.String(), nullable=True),
    sa.Column('public_id', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('lastname', sa.String(length=120), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('products')
    # ### end Alembic commands ###
