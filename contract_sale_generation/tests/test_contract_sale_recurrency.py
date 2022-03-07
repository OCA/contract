# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun.api import freeze_time

from odoo import fields
from odoo.tests import Form
from odoo.tests.common import SavepointCase

from .common import ContractSaleCommon


def to_date(date):
    return fields.Date.to_date(date)


today = "2020-01-15"


class TestContractSale(ContractSaleCommon, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract_obj = cls.env["contract.contract"]

    @classmethod
    def _create_contract(cls):
        cls.contract = cls.contract.create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
            }
        )
        with Form(cls.contract) as contract_form:
            contract_form.partner_id = cls.partner
            contract_form.generation_type = "sale"
            contract_form.group_id = cls.analytic_account
        cls.contract = contract_form.save()

    def test_contract_next_date(self):
        """
        Change recurrence to weekly
        Check the recurring next date value on lines
        """
        with freeze_time(today):
            self._create_contract()
        self.contract.recurring_rule_type = "weekly"
        with freeze_time(today):
            with Form(self.contract) as contract_form:
                with contract_form.contract_line_ids.new() as line_form:
                    line_form.product_id = self.product_1
                    line_form.name = "Services from #START# to #END#"
                    line_form.quantity = 1
                    line_form.price_unit = 100.0
                    line_form.discount = 50
                    line_form.recurring_rule_type = "weekly"

        with freeze_time(today):
            with Form(self.contract) as contract_form:
                with contract_form.contract_line_ids.new() as line_form:
                    line_form.product_id = self.product_1
                    line_form.name = "Services from #START# to #END#"
                    line_form.quantity = 2
                    line_form.price_unit = 50.0
                    line_form.recurring_rule_type = "weekly"

        self.assertEqual(
            fields.Date.to_date("2020-01-15"), self.contract.recurring_next_date
        )

        self.contract.recurring_create_sale()
        self.assertEqual(
            fields.Date.to_date("2020-01-22"), self.contract.recurring_next_date
        )
        self.contract.recurring_create_sale()
        self.assertEqual(
            fields.Date.to_date("2020-01-29"), self.contract.recurring_next_date
        )
