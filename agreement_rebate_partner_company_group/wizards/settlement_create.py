# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AgreementSettlementCreateWiz(models.TransientModel):
    _inherit = "agreement.settlement.create.wiz"

    def _partner_domain(self, agreement):
        if not agreement.partner_id.company_group_member_ids:
            return super()._partner_domain(agreement)
        # Try replace only child_of part in original domain
        orig_domain = ("partner_id", "child_of", agreement.partner_id.ids)
        domain = super()._partner_domain(agreement)
        pos = 0
        if orig_domain in domain:
            pos = domain.index(orig_domain)
            domain.remove(orig_domain)
        domain.insert(
            pos, ("partner_id", "in", agreement.partner_id.company_group_member_ids.ids)
        )
        return domain
