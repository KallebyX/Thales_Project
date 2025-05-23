"""Marca services como pacote

Revision ID: 1abcdef5e65d
Revises: bfd8c78e81ef
Create Date: 2025-04-27 20:46:42.264548

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1abcdef5e65d'
down_revision = 'bfd8c78e81ef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.create_index('ix_patient_user_cpf', ['user_id', 'cpf'], unique=False)

    with op.batch_alter_table('uploaded_ecg', schema=None) as batch_op:
        batch_op.create_index('ix_ecg_user_patient', ['user_id', 'patient_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('uploaded_ecg', schema=None) as batch_op:
        batch_op.drop_index('ix_ecg_user_patient')

    with op.batch_alter_table('patient', schema=None) as batch_op:
        batch_op.drop_index('ix_patient_user_cpf')

    # ### end Alembic commands ###
