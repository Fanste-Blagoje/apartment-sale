"""contract model and new relations with new tables

Revision ID: 28a7205c50b7
Revises: a994c6cbb923
Create Date: 2021-11-04 10:31:35.628785

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '28a7205c50b7'
down_revision = 'a994c6cbb923'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tbl_contract',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('customer_id', sa.Integer(), nullable=True),
    sa.Column('contract_number', sa.String(length=30), nullable=False),
    sa.Column('payment_method', sa.Enum('cash', 'credit', 'on_installment', 'participation', name='paymentmethodenum'), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date_of_creation', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('date_of_update', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted', sa.Boolean(), server_default=sa.text('false'), nullable=True),
    sa.ForeignKeyConstraint(['customer_id'], ['tbl_customer.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['tbl_user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('contract_number')
    )
    op.add_column('tbl_apartment', sa.Column('photo', sa.Text(), nullable=True))
    op.add_column('tbl_customer_apartment', sa.Column('contract_id', sa.Integer(), nullable=True))
    op.add_column('tbl_customer_apartment', sa.Column('approved_by', sa.Integer(), nullable=True))
    op.add_column('tbl_customer_apartment', sa.Column('approved', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    op.alter_column('tbl_customer_apartment', 'apartment_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.alter_column('tbl_customer_apartment', 'customer_id',
               existing_type=mysql.INTEGER(),
               nullable=True)
    op.create_foreign_key(None, 'tbl_customer_apartment', 'tbl_user', ['approved_by'], ['id'])
    op.create_foreign_key(None, 'tbl_customer_apartment', 'tbl_contract', ['contract_id'], ['id'])
    op.drop_column('tbl_customer_apartment', 'contract_number')
    op.drop_column('tbl_customer_apartment', 'contract_date')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tbl_customer_apartment', sa.Column('contract_date', sa.DATE(), nullable=True))
    op.add_column('tbl_customer_apartment', sa.Column('contract_number', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'tbl_customer_apartment', type_='foreignkey')
    op.drop_constraint(None, 'tbl_customer_apartment', type_='foreignkey')
    op.alter_column('tbl_customer_apartment', 'customer_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.alter_column('tbl_customer_apartment', 'apartment_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
    op.drop_column('tbl_customer_apartment', 'approved')
    op.drop_column('tbl_customer_apartment', 'approved_by')
    op.drop_column('tbl_customer_apartment', 'contract_id')
    op.drop_column('tbl_apartment', 'photo')
    op.drop_table('tbl_contract')
    # ### end Alembic commands ###
