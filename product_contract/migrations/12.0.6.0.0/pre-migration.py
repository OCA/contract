# Copyright 2020 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Copy the product template contract on their variants."""
    contract_key = "property_contract_template_id"  # TODO: check that mig (do in SQL?)

    for company in env["res.company"].with_context(active_test=False).search([]):
        company_env = env["product.template"].with_context(
            force_company=company.id, active_test=False
        )
        templates = company_env.search([(contract_key, "!=", False)])
        for template in templates:
            template.variant_ids.write({contract_key: template[contract_key].id})
