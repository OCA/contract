# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestProduct(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_product1 = self.env["product.template"].create(
            {"name": "TestProduct"}
        )
        self.test_product2 = self.env["product.product"].create({"name": "TestProduct"})

    # TEST 01: Test onchange_type product.template
    def test_product_template_onchange_type(self):
        product_01 = self.test_product1
        product_01.is_serviceprofile = True
        product_01.onchange_type()
        self.assertEqual(product_01.type, "service")

    # TEST 02: Test onchange_type product.product
    def test_product_product_onchange_type(self):
        product_02 = self.test_product2
        product_02.is_serviceprofile = True
        product_02.onchange_type()
        self.assertEqual(product_02.type, "service")
