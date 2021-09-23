# Copyright 2016 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import exceptions
from odoo.tests.common import SavepointCase


class TestContractVariableQuantity(SavepointCase):
    at_install = False
    post_install = True

    def setUp(self):
        super().setUp()
        self.partner = self.env["res.partner"].create({"name": "Test partner"})
        self.product = self.env["product.product"].create({"name": "Test product"})
        self.contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": self.partner.id,
                "pricelist_id": self.partner.property_product_pricelist.id,
            }
        )
        self.formula = self.env["contract.line.qty.formula"].create(
            {
                "name": "Test formula",
                # For testing each of the possible variables
                "code": 'env["res.users"]\n'
                'context.get("lang")\n'
                "user.id\n"
                "line.qty_type\n"
                "contract.id\n"
                "quantity\n"
                "period_first_date\n"
                "period_last_date\n"
                "invoice_date\n"
                "result = 12",
            }
        )
        self.contract_line = self.env["contract.line"].create(
            {
                "contract_id": self.contract.id,
                "product_id": self.product.id,
                "name": "Test",
                "qty_type": "variable",
                "qty_formula_id": self.formula.id,
                "quantity": 1,
                "uom_id": self.product.uom_id.id,
                "price_unit": 100,
                "discount": 50,
                "recurring_rule_type": "monthly",
                "recurring_interval": 1,
                "date_start": "2016-02-15",
                "recurring_next_date": "2016-02-29",
            }
        )

    def test_check_invalid_code(self):
        with self.assertRaises(exceptions.ValidationError):
            self.formula.code = "sdsds"

    def test_check_no_return_value(self):
        with self.assertRaises(exceptions.ValidationError):
            self.formula.code = "user.id"

    def test_check_variable_quantity(self):
        self.contract.recurring_create_invoice()
        invoice = self.contract._get_related_invoices()
        self.assertEqual(invoice.invoice_line_ids[0].quantity, 12)

    def test_check_skip_zero_qty(self):
        self.formula.code = "result=0"
        self.contract.skip_zero_qty = True
        invoice = self.contract.recurring_create_invoice()
        self.assertFalse(invoice.invoice_line_ids)
        self.contract.skip_zero_qty = False
        invoice = self.contract.recurring_create_invoice()
        self.assertAlmostEqual(invoice.invoice_line_ids[0].quantity, 0.0)
