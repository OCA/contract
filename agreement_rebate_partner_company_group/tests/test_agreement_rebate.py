# Copyright 2022 Tecnativa - Carlos Dauden
# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import tagged

from odoo.addons.agreement_rebate.tests.test_agreement_rebate import (
    TestAgreementRebateBase,
)


@tagged("-at_install", "post_install")
class TestAgreementRebatePartnerCompanyGroup(TestAgreementRebateBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner_group = cls.env["res.partner"].create(
            {"name": "partner test rebate group", "ref": "TST-G01"}
        )
        cls.partner_1.company_group_id = cls.partner_group
        cls.partner_2.company_group_id = cls.partner_group

    def test_create_settlement_wo_filters_global_company_group(self):
        """Global rebate without filters apply to all company group members"""
        # Total by invoice: 3800 amount invoiced
        # 2 invoice members: 3800 * 2 = 7600

        # Global rebate without filters
        agreement_global = self.create_agreements_rebate("global", self.partner_group)
        agreement_global.rebate_line_ids = False
        settlement_wiz = self.create_settlement_wizard(agreement_global)
        settlements = self.get_settlements_from_action(
            settlement_wiz.action_create_settlement()
        )
        self.assertEqual(len(settlements), 1)
        self.assertEqual(settlements.amount_invoiced, 7600)
        self.assertEqual(settlements.amount_rebate, 760)
