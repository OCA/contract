# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        """
        UPDATE mail_activity activity
           SET summary = 'Recurring ' || contract.generation_type || ' failed'
          FROM contract_contract contract
         WHERE activity.res_model = 'contract.contract'
           AND activity.res_id = contract.id
           AND activity.summary = 'Recurring invoice failed'
           AND contract.generation_type != 'invoice'
        """
    )
