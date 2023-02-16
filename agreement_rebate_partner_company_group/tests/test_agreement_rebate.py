# Copyright 2022 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.agreement_rebate.tests.test_agreement_rebate import TestAgreementRebate


class TestAgreementRebatePartnerCompanyGroup(TestAgreementRebate):
    def setUp(self):
        super().setUp()
        self.Partner = self.env["res.partner"]
        self.partner_group = self.Partner.create(
            {"name": "partner test rebate group", "ref": "TST-G01"}
        )
        self.partner_member_1 = self.Partner.create(
            {
                "name": "partner test rebate member 1",
                "ref": "TST-M001",
                "company_group_id": self.partner_group.id,
            }
        )
        self.partner_member_2 = self.Partner.create(
            {
                "name": "partner test rebate  member 2",
                "ref": "TST-M002",
                "company_group_id": self.partner_group.id,
            }
        )
        self.invoice_member_1 = self.create_invoice(self.partner_member_1)
        self.invoice_member_2 = self.create_invoice(self.partner_member_2)

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
