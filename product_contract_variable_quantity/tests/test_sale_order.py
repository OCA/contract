# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product1 = cls.env.ref("product.product_product_1")
        cls.product1.is_contract = True
        cls.sale = cls.env.ref("sale.sale_order_2")
        cls.contract_template1 = cls.env["contract.template"].create(
            {"name": "Template 1"}
        )
        cls.formula = cls.env["contract.line.qty.formula"].create(
            {
                "name": "Test formula",
                # For testing each of the possible variables
                "code": 'env["res.users"]\n'
                'context.get("lang")\n'
                "user.id\n"
                "line.qty_type\n"
                "contract.id\n"
                "invoice.id\n"
                "result = 12",
            }
        )
        cls.product1.with_company(cls.sale.company_id).write(
            {
                "recurrence_number": 12,
                "property_contract_template_id": cls.contract_template1.id,
                "qty_formula_id": cls.formula.id,
                "qty_type": "variable",
            }
        )
        cls.order_line1 = cls.sale.order_line.filtered(
            lambda line: line.product_id == cls.product1
        )
        cls.sale.order_line._compute_product_contract_data()

    def test_change_is_contract(self):
        product_tmpl = self.product1.product_tmpl_id
        product_tmpl.is_contract = False
        self.assertFalse(product_tmpl.qty_type)

    def test_onchange_product_id(self):
        self.assertEqual(self.order_line1.qty_formula_id, self.product1.qty_formula_id)
        self.assertEqual(self.order_line1.qty_type, self.product1.qty_type)

    def test_action_confirm(self):
        self.sale.action_confirm()
        contract = self.order_line1.contract_id
        contract_line = contract.contract_line_ids.filtered(
            lambda line: line.product_id == self.product1
        )
        self.assertEqual(contract_line.qty_formula_id, self.product1.qty_formula_id)
        self.assertEqual(contract_line.qty_type, self.product1.qty_type)
        self.assertEqual(contract_line.qty_type, "variable")
        self.product1.product_tmpl_id.qty_type = "fixed"
        contract_line._onchange_product_id_recurring_info()
        self.assertEqual(contract_line.qty_type, "fixed")
