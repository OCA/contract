# Copyright 2018 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractSaleInvoicing(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super(TestContractSaleInvoicing, cls).setUpClass()
        cls.contract_obj = cls.env['contract.contract']
        cls.account_invoice_line_obj = cls.env['account.invoice.line']
        cls.contract.group_id = \
            cls.env['account.analytic.account'].search([], limit=1)
        cls.product_so = cls.env.ref(
            'product.product_product_1')
        cls.product_so.invoice_policy = 'order'
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'partner_invoice_id': cls.partner.id,
            'partner_shipping_id': cls.partner.id,
            'order_line': [(0, 0, {'name': cls.product_so.name,
                                   'product_id': cls.product_so.id,
                                   'product_uom_qty': 2,
                                   'product_uom': cls.product_so.uom_id.id,
                                   'price_unit': cls.product_so.list_price})],
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'analytic_account_id': cls.contract.group_id.id,
            'date_order': '2016-02-15',
        })

    def test_not_sale_invoicing(self):
        self.contract.invoicing_sales = False
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, 'to invoice')

    def test_sale_invoicing(self):
        self.contract.invoicing_sales = True
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, 'invoiced')

    def test_contract_sale_invoicing_without(self):
        self.contract.invoicing_sales = True
        self.sale_order.analytic_account_id = False
        self.sale_order.action_confirm()
        self.contract.recurring_create_invoice()
        self.assertEqual(self.sale_order.invoice_status, 'to invoice')

    def test_action_view_sales_orders(self):
        self.contract._compute_sale_order_count()
        self.contract.action_view_sales_orders()

    def test_csi_group_by_so_aa(self):
        contract_copy = self.contract.copy({
            'filter_with': 'analytic_account',
            'group_by': 'sale_order',
            'invoicing_sales': True
        })
        so_val = {
            'date_order': '2016-02-15',
            'contract_id': contract_copy.id
        }
        sale_order_copy1 = self.sale_order.copy(so_val)
        sale_order_copy2 = self.sale_order.copy(so_val)
        sale_order_copy1.action_confirm()
        sale_order_copy2.action_confirm()
        self.contract_obj.cron_recurring_create_invoice()
        contract_line_list = [contract_copy.contract_line_ids.id,
                              self.contract.contract_line_ids.id]
        invoice_line = self.account_invoice_line_obj.search([
            ('contract_line_id', 'in', contract_line_list)], order='id asc')

        self.assertEqual(invoice_line[0].quantity, 1)
        self.assertEqual(invoice_line[0].product_id,
                         sale_order_copy1.order_line.product_id)
        self.assertEqual(invoice_line[1].quantity, 1)
        self.assertEqual(invoice_line[1].product_id,
                         sale_order_copy1.order_line.product_id)

    def test_contract_sale_invoicing(self):
        contract_copy = self.contract.copy({
            'filter_with': 'contract',
            'group_by': 'contract',
            'invoicing_sales': True
        })
        so_val = {
            'date_order': '2016-02-15',
            'contract_id': contract_copy.id
        }
        sale_order_copy1 = self.sale_order.copy(so_val)
        sale_order_copy2 = self.sale_order.copy(so_val)
        sale_order_copy1.action_confirm()
        sale_order_copy2.action_confirm()
        self.contract_obj.cron_recurring_create_invoice()
        contract_line_list = [contract_copy.contract_line_ids.id,
                              self.contract.contract_line_ids.id]
        invoice_line = self.account_invoice_line_obj.search([
            ('contract_line_id', 'in', contract_line_list)], order='id asc')
        self.assertEqual(invoice_line[0].quantity, 1)
        self.assertEqual(invoice_line[0].product_id,
                         sale_order_copy1.order_line.product_id)
        self.assertEqual(invoice_line[1].quantity, 1)
        self.assertEqual(invoice_line[1].product_id,
                         sale_order_copy1.order_line.product_id)
        self.assertEqual(invoice_line[2].product_id,
                         sale_order_copy1.order_line.product_id)
