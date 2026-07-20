# Copyright 2016 Antiun Ingenieria S.L. - Antonio Espinosa
# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def pre_init_hook(env):
    """Create and prefill payment_mode_id before stored compute runs."""
    openupgrade.add_columns(
        env,
        [
            (
                "contract.contract",
                "payment_mode_id",
                "many2one",
                None,
                "contract_contract",
            )
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE contract_contract AS c
           SET payment_mode_id = CASE
               WHEN c.contract_type = 'purchase' THEN
                   (rp.supplier_payment_mode_id ->> c.company_id::text)::int
               ELSE (rp.customer_payment_mode_id ->> c.company_id::text)::int
           END
        FROM res_partner rp
        WHERE rp.id = c.partner_id AND c.payment_mode_id IS NULL
        """,
    )
