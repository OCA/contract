# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2023 Tecnativa - Carolina Fernandez
# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command

from odoo.addons.base.tests.common import BaseCommon


@freeze_time("2016-02-28")
class TestContractSaleInvoicing(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.contract.group_id = cls.env["account.analytic.account"].search([], limit=1)
        cls.other_analytic_account = cls.env["account.analytic.account"].search(
            [("id", "!=", cls.contract.group_id.id)], limit=1
        )
        cls.product_so_1 = cls.env.ref("product.product_product_1")
        cls.product_so_2 = cls.env.ref("product.product_product_2")
        cls.product_so_1.invoice_policy = "order"
        cls.product_so_2.invoice_policy = "order"
        cls.sale_order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "partner_shipping_id": cls.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "name": cls.product_so_1.name,
                            "product_id": cls.product_so_1.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.product_so_1.uom_id.id,
                            "price_unit": cls.product_so_1.list_price,
                            "analytic_distribution": {
                                cls.contract.group_id.id: 100.0,
                            },
                        }
                    ),
                    Command.create(
                        {
                            "name": cls.product_so_2.name,
                            "product_id": cls.product_so_2.id,
                            "product_uom_qty": 5,
                            "product_uom": cls.product_so_2.uom_id.id,
                            "price_unit": cls.product_so_2.list_price,
                            "analytic_distribution": {
                                cls.contract.group_id.id: 100.0,
                            },
                        }
                    ),
                ],
                "pricelist_id": cls.partner.property_product_pricelist.id,
            }
        )

    def test_not_sale_invoicing(self):
        """
        Do not invoice Sale Order when contract configuration is not set
        """
        self.contract.invoicing_sales = False
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, "to invoice")

    def test_sale_invoicing(self):
        """
        Do invoice Sale Order that matches on analytic account
        """
        self.contract.invoicing_sales = True
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, "invoiced")

    def test_contract_sale_invoicing_without(self):
        """
        Do not invoice Sale Order that doesn't match on analytic account
        """
        self.contract.invoicing_sales = True
        self.sale_order.order_line.write({"analytic_distribution": {}})
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, "to invoice")

    def test_contract_sale_invoicing_mixed(self):
        """
        Do not invoice Sale Order where its lines match partially on analytic account
        """
        self.contract.invoicing_sales = True
        self.sale_order.order_line.write(
            {
                "analytic_distribution": {
                    self.contract.group_id.id: 50.0,
                    self.other_analytic_account.id: 50.0,
                }
            }
        )
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, "to invoice")

    def test_contract_sale_invoicing_mixed_multi_line(self):
        """
        Do invoice Sale Order Lines where lines match on analytic account
        """
        self.contract.invoicing_sales = True
        line1, line2 = self.sale_order.order_line
        line1.analytic_distribution = {}
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(line1.invoice_status, "to invoice")
        self.assertEqual(line2.invoice_status, "invoiced")
