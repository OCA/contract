# Copyright 2026 Binhex (<https://www.binhex.cloud>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # PR OCA/contract#1060 made subscription_template_id a company-dependent field on
    # product.template, but was never forward-ported beyond the version it targeted
    # (v14). In Odoo 18.0, company-dependent fields are stored in a jsonb column instead
    # of ir_property records. Since the forward-port never happened, the migration from
    # ir_property to jsonb was not performed automatically, leaving the field empty.
    # This query backfills product_template.subscription_template_id from the legacy
    # ir_property rows so no data is lost after the upgrade.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET subscription_template_id = split_part(ip.value_reference, ',', 2)::integer
        FROM ir_property ip
        WHERE ip.name = 'subscription_template_id'
          AND pt.id = split_part(ip.res_id, ',', 2)::integer
        """,
    )
