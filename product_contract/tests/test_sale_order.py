# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.fields import Date


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.product1 = self.env.ref('product.product_product_1')
        self.product2 = self.env.ref('product.product_product_2')
        self.sale = self.env.ref('sale.sale_order_2')
        self.contract_template1 = self.env['contract.template'].create(
            {'name': 'Template 1'}
        )
        self.contract_template2 = self.env['contract.template'].create(
            {
                'name': 'Template 2',
                'contract_line_ids': [
                    (
                        0,
                        0,
                        {
                            'product_id': self.product2.id,
                            'name': 'Services from #START# to #END#',
                            'quantity': 1,
                            'uom_id': self.product2.uom_id.id,
                            'price_unit': 100,
                            'discount': 50,
                            'recurring_rule_type': 'yearly',
                            'recurring_interval': 1,
                        },
                    )
                ],
            }
        )
        self.product1.write(
            {
                'is_contract': True,
                'default_qty': 12,
                'recurring_rule_type': "monthlylastday",
                'contract_template_id': self.contract_template1.id,
            }
        )
        self.product2.write(
            {
                'is_contract': True,
                'contract_template_id': self.contract_template2.id,
            }
        )
        self.order_line1 = self.sale.order_line.filtered(
            lambda l: l.product_id == self.product1
        )
        self.order_line1.date_start = '2018-01-01'
        self.order_line1.product_uom_qty = 12
        pricelist = self.sale.partner_id.property_product_pricelist.id
        self.contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract 2",
                "partner_id": self.sale.partner_id.id,
                "pricelist_id": pricelist,
                "contract_type": "sale",
                "contract_template_id": self.contract_template1.id,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product1.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": self.product1.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2016-02-15",
                            "recurring_next_date": "2016-02-29",
                        },
                    )
                ],
            }
        )
        self.contract_line = self.contract.contract_line_ids[0]

    def test_compute_is_contract(self):
        """Sale Order should have is_contract true if one of its lines is
        contract"""
        self.assertTrue(self.sale.is_contract)

    def test_action_confirm(self):
        """ It should create a contract for each contract template used in
        order_line """
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        contracts = self.sale.order_line.mapped('contract_id')
        self.assertEqual(len(contracts), 2)
        self.assertEqual(
            self.order_line1.contract_id.contract_template_id,
            self.contract_template1,
        )
        contract_line = self.order_line1.contract_id.contract_line_ids
        self.assertEqual(contract_line.date_start, Date.to_date('2018-01-01'))
        self.assertEqual(contract_line.date_end, Date.to_date('2018-12-31'))
        self.assertEqual(
            contract_line.recurring_next_date, Date.to_date('2018-01-31')
        )

    def test_contract_company(self):
        """
        contract company must be the sale order company and not the user one
        """
        self.assertTrue(self.sale.company_id)
        other_company = self.env['res.company'].create(
            {'name': 'other company', 'parent_id': self.sale.company_id.id}
        )
        self.sale.company_id = other_company
        self.sale.action_confirm()
        contracts = self.sale.order_line.mapped('contract_id')
        self.assertEqual(contracts.mapped('company_id'), other_company)

    def test_sale_order_invoice_status(self):
        """
        sale line linked to contracts must not be invoiced from sale order
        """
        self.sale.action_confirm()
        self.assertEqual(self.order_line1.invoice_status, 'no')
        invoice = self.order_line1.contract_id.recurring_create_invoice()
        self.assertTrue(invoice)
        self.assertEqual(self.order_line1.invoice_qty, 1)
        self.assertEqual(self.order_line1.qty_to_invoice, 0)

    def test_action_confirm_without_contract_creation(self):
        """ It should create a contract for each contract template used in
        order_line """
        self.sale.company_id.create_contract_at_sale_order_confirmation = False
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(len(self.sale.order_line.mapped('contract_id')), 0)
        self.assertTrue(self.sale.need_contract_creation)
        self.sale.action_create_contract()
        self.assertEqual(len(self.sale.order_line.mapped('contract_id')), 2)
        self.assertFalse(self.sale.need_contract_creation)
        self.assertEqual(
            self.order_line1.contract_id.contract_template_id,
            self.contract_template1,
        )
        contract_line = self.order_line1.contract_id.contract_line_ids
        self.assertEqual(contract_line.date_start, Date.to_date('2018-01-01'))
        self.assertEqual(contract_line.date_end, Date.to_date('2018-12-31'))
        self.assertEqual(
            contract_line.recurring_next_date, Date.to_date('2018-01-31')
        )

    def test_sale_contract_count(self):
        """It should count contracts as many different contract template used
        in order_line"""
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(self.sale.contract_count, 2)

    def test_onchange_product(self):
        """ It should get recurrence invoicing info to the sale line from
        its product """
        self.order_line1.onchange_product()
        self.assertEqual(
            self.order_line1.recurring_rule_type,
            self.product1.recurring_rule_type,
        )
        self.assertEqual(
            self.order_line1.recurring_invoicing_type,
            self.product1.recurring_invoicing_type,
        )
        self.assertEqual(self.order_line1.date_end, Date.to_date('2018-12-31'))

    def test_check_contract_sale_partner(self):
        """Can't link order line to a partner contract different then the
        order one"""
        contract2 = self.env['contract.contract'].create(
            {
                'name': 'Contract',
                'contract_template_id': self.contract_template2.id,
                'partner_id': self.sale.partner_id.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.order_line1.contract_id = contract2

    def test_check_contract_sale_contract_template(self):
        """Can't link order line to a contract with different contract
        template then the product one"""
        contract1 = self.env['contract.contract'].create(
            {
                'name': 'Contract',
                'partner_id': self.env.user.partner_id.id,
                'contract_template_id': self.contract_template1.id,
            }
        )
        with self.assertRaises(ValidationError):
            self.order_line1.contract_id = contract1

    def test_no_contract_proudct(self):
        """it should create contract for only product contract"""
        self.product1.is_contract = False
        self.sale.action_confirm()
        self.assertFalse(self.order_line1.contract_id)

    def test_sale_order_line_invoice_status(self):
        """Sale order line for contract product should have nothing to
        invoice as status"""
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(self.order_line1.invoice_status, 'no')

    def test_sale_order_invoice_status(self):
        """Sale order with only contract product should have nothing to
        invoice status directtly"""
        self.sale.order_line.filtered(
            lambda line: not line.product_id.is_contract
        ).unlink()
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(self.sale.invoice_status, 'no')

    def test_sale_order_create_invoice(self):
        """Should not invoice contract product on sale order create invoice"""
        self.product2.is_contract = False
        self.product2.invoice_policy = 'order'
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.sale.action_invoice_create()
        self.assertEqual(len(self.sale.invoice_ids), 1)
        invoice_line = self.sale.invoice_ids.invoice_line_ids.filtered(
            lambda line: line.product_id.is_contract
        )
        self.assertEqual(len(invoice_line), 0)

    def test_link_contract_invoice_to_sale_order(self):
        """It should link contract invoice to sale order"""
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        invoice = self.order_line1.contract_id.recurring_create_invoice()
        self.assertTrue(invoice in self.sale.invoice_ids)

    def test_contract_upsell(self):
        """Should stop contract line at sale order line start date"""
        self.order_line1.contract_id = self.contract
        self.order_line1.contract_line_id = self.contract_line
        self.contract_line.date_end = Date.today() + relativedelta(months=4)
        self.contract_line.is_auto_renew = True
        self.order_line1.date_start = "2018-06-01"
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertEqual(
            self.contract_line.date_end, Date.to_date("2018-05-31")
        )
        self.assertFalse(self.contract_line.is_auto_renew)
        new_contract_line = self.env['contract.line'].search(
            [('sale_order_line_id', '=', self.order_line1.id)]
        )
        self.assertEqual(
            self.contract_line.successor_contract_line_id, new_contract_line
        )
        self.assertEqual(
            new_contract_line.predecessor_contract_line_id, self.contract_line
        )

    def test_contract_upsell_2(self):
        """Should stop contract line at sale order line start date"""
        self.order_line1.contract_id = self.contract
        self.order_line1.contract_line_id = self.contract_line
        self.contract_line.write(
            {
                'date_start': "2018-06-01",
                'recurring_next_date': "2018-06-01",
                'date_end': False,
            }
        )
        self.order_line1.date_start = "2018-06-01"
        self.order_line1.onchange_product()
        self.sale.action_confirm()
        self.assertFalse(self.contract_line.date_end)
        self.assertTrue(self.contract_line.is_canceled)

    def test_onchange_product_id_recurring_info(self):
        self.product2.write(
            {
                'recurring_rule_type': 'monthly',
                'recurring_invoicing_type': 'pre-paid',
                'is_auto_renew': True,
                'default_qty': 12,
                'termination_notice_interval': '6',
                'termination_notice_rule_type': 'weekly',
            }
        )
        self.contract_line.write(
            {
                'date_start': Date.today(),
                'date_end': Date.today() + relativedelta(years=1),
                'recurring_next_date': Date.today(),
                'product_id': self.product2.id,
            }
        )
        self.contract_line._onchange_product_id_recurring_info()
        self.assertEqual(self.contract_line.recurring_rule_type, 'monthly')
        self.assertEqual(
            self.contract_line.recurring_invoicing_type, 'pre-paid'
        )
        self.assertEqual(self.contract_line.recurring_interval, 1)
        self.assertEqual(self.contract_line.is_auto_renew, True)
        self.assertEqual(self.contract_line.auto_renew_interval, 12)
        self.assertEqual(self.contract_line.auto_renew_rule_type, 'monthly')
        self.assertEqual(self.contract_line.termination_notice_interval, 6)
        self.assertEqual(
            self.contract_line.termination_notice_rule_type, 'weekly'
        )

    def test_action_show_contracts(self):
        self.sale.action_confirm()
        action = self.sale.action_show_contracts()
        self.assertEqual(
            self.env['contract.contract'].search(action['domain']),
            self.sale.order_line.mapped('contract_id'),
        )
