"""add netfee

Revision ID: 7a0fe7de09fa
Revises: 48b989661635
Create Date: 2024-06-02 13:36:13.826749

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel             # NEW


# revision identifiers, used by Alembic.
revision = '7a0fe7de09fa'
down_revision = '48b989661635'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('claim', sa.Column('net_fee', sa.Float(), nullable=False))
    op.create_index(op.f('ix_provider_npi'), 'claim', ['provider_npi'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('claim', 'net_fee')
    op.drop_index(op.f('ix_provider_npi'), table_name='claim')
    # ### end Alembic commands ###
