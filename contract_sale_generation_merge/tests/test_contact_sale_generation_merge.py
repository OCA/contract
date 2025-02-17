# Copyright 2025 Patryk Pyczko (APSL-Nagarro)<ppyczko@apsl.net>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import TransactionCase


class TestContractSaleGenerationMerge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract_model = cls.env["contract.contract"]
        cls.sale_order_model = cls.env["sale.order"]
        cls.sale_order_line_model = cls.env["sale.order.line"]
        cls.contract_line_model = cls.env["contract.line"]
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Product",
                "type": "service",
            }
        )

        cls.contract = cls.contract_model.create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "merge_sales_orders": True,
            }
        )

        cls.contract_line = cls.contract_line_model.create(
            {
                "contract_id": cls.contract.id,
                "name": "Test Contract Line",
                "product_id": cls.product.id,
                "price_unit": 100.0,
                "uom_id": cls.product.uom_id.id,
                "recurring_next_date": datetime.today(),
            }
        )

        cls.commitment_date = datetime.today()
        cls.existing_order = cls.sale_order_model.create(
            {
                "partner_id": cls.partner.id,
                "state": "draft",
                "commitment_date": cls.commitment_date,
            }
        )

    def test_create_new_sale_order(self):
        """Should create a new sale order if no existing order is found."""
        self.contract._recurring_create_sale()

        sale_orders = self.sale_order_model.search(
            [("partner_id", "=", self.partner.id)]
        )
        self.assertEqual(
            len(sale_orders), 1, "A new sale order should have been created."
        )

    def test_merge_existing_sale_order(self):
        """Should merge with an existing sale order if merge_sales_orders is enabled."""
        self.contract._recurring_create_sale()

        sale_orders = self.sale_order_model.search(
            [("partner_id", "=", self.partner.id)]
        )
        self.assertEqual(
            len(sale_orders),
            1,
            "Contract lines should have merged into the existing order.",
        )
        self.assertEqual(
            len(self.existing_order.order_line),
            1,
            "A contract line should have been added.",
        )

    def test_no_merge_when_disabled(self):
        """Should create a new sale order if merge_sales_orders is disabled."""
        self.contract.merge_sales_orders = False

        self.contract._recurring_create_sale()

        sale_orders = self.sale_order_model.search(
            [("partner_id", "=", self.partner.id)]
        )
        self.assertEqual(
            len(sale_orders), 2, "A new sale order should have been created."
        )

    def test_ignore_canceled_orders(self):
        """Should not merge with an order that has a 'cancel' state."""
        self.sale_order_model.create(
            {
                "partner_id": self.partner.id,
                "state": "cancel",
                "commitment_date": self.commitment_date,
            }
        )

        self.contract._recurring_create_sale()

        sale_orders = self.sale_order_model.search(
            [("partner_id", "=", self.partner.id), ("state", "!=", "cancel")]
        )
        self.assertEqual(
            len(sale_orders), 1, "A new sale order should have been created."
        )

    def test_contract_lines_added_correctly(self):
        """Should add contract lines correctly to an existing order."""
        self.contract._add_contract_lines(self.existing_order)

        self.assertEqual(
            len(self.existing_order.order_line),
            1,
            "A contract line should have been added.",
        )
