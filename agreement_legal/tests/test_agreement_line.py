# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAgreementLine(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_customer = self.env["res.partner"].create({"name": "TestCustomer"})
        self.agreement_type = self.env["agreement.type"].create(
            {
                "name": "Test Agreement Type",
                "domain": "sale",
            }
        )
        self.test_agreement = self.env["agreement"].create(
            {
                "name": "TestAgreement",
                "description": "Test",
                "special_terms": "Test",
                "partner_id": self.test_customer.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today() + timedelta(days=365),
            }
        )
        self.test_product1 = self.env["product.product"].create({"name": "TEST1"})
        self.test_product2 = self.env["product.product"].create({"name": "TEST2"})
        self.test_line = self.env["agreement.line"].create(
            {
                "product_id": self.test_product1.id,
                "name": "Test",
                "uom_id": 1,
                "agreement_id": self.test_agreement.id,
            }
        )

    # TEST 01: Set line product onchange method
    def test_onchange_product_id(self):
        line_01 = self.test_line
        line_01.product_id = self.test_product2.id
        line_01._onchange_product_id()
        self.assertEqual(line_01.name, "TEST2")
