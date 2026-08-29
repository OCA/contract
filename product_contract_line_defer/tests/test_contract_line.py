# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.contract.tests.test_contract import TestContractBase


class Test(BaseCommon, TestContractBase):
    """
    Tests for contract.line
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
            }
        )
        contract_template = cls.env["contract.template"].create({"name": "Template 1"})
        cls.product_1.write(
            {
                "service_tracking": "no",
                "is_contract": True,
                "property_contract_template_id": contract_template.id,
                "is_deferred": True,
            }
        )

    def test_contract_line_defer(self):
        sale_form = Form(self.order)
        with sale_form.order_line.new() as line_form:
            line_form.product_id = self.product_1
        sale_form.save()
        self.assertTrue(self.order.order_line.is_deferred)
        self.order.action_confirm()
        contract = self.order.order_line.mapped("contract_id")
        self.assertTrue(contract.contract_line_ids.is_deferred)
