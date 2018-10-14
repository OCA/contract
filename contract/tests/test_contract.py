# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Carlos Dauden
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from mock import patch
from contextlib import contextmanager

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common

from odoo.addons.contract.models.account_analytic_account \
    import _logger as aaa_logger


class TestContractBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractBase, cls).setUpClass()
        cls.partner = cls.env.ref('base.res_partner_2')
        cls.product = cls.env.ref('product.product_product_2')
        cls.product.taxes_id += cls.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1)
        cls.product.description_sale = 'Test description sale'
        cls.template_vals = {
            'recurring_rule_type': 'yearly',
            'recurring_interval': 12345,
            'name': 'Test Contract Template',
        }
        cls.template = cls.env['account.analytic.contract'].create(
            cls.template_vals,
        )
        cls.contract = cls.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'partner_id': cls.partner.id,
            'pricelist_id': cls.partner.property_product_pricelist.id,
            'recurring_invoices': True,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29',
        })
        cls.line_vals = {
            'analytic_account_id': cls.contract.id,
            'product_id': cls.product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': cls.product.uom_id.id,
            'price_unit': 100,
            'discount': 50,
        }
        cls.acct_line = cls.env['account.analytic.invoice.line'].create(
            cls.line_vals,
        )

    @contextmanager
    def assertExceptionLogged(self, exception_type):
        with patch.object(aaa_logger, 'exception') as mocked_log:
            yield mocked_log
        self.assertTrue(any('%s:' % exception_type.__name__ in args[0]
                            for args, kw in mocked_log.call_args_list))


class TestContract(TestContractBase):
    def _add_template_line(self, overrides=None):
        if overrides is None:
            overrides = {}
        vals = self.line_vals.copy()
        vals['analytic_account_id'] = self.template.id
        vals.update(overrides)
        return self.env['account.analytic.contract.line'].create(vals)

    def test_check_discount(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write({'discount': 120})

    def test_automatic_price(self):
        self.acct_line.automatic_price = True
        self.product.list_price = 1100
        self.assertEqual(self.acct_line.price_unit, 1100)
        # Try to write other price
        self.acct_line.price_unit = 10
        self.acct_line.refresh()
        self.assertEqual(self.acct_line.price_unit, 1100)
        # Now disable automatic price
        self.acct_line.automatic_price = False
        self.acct_line.price_unit = 10
        self.acct_line.refresh()
        self.assertEqual(self.acct_line.price_unit, 10)

    def test_contract(self):
        self.assertAlmostEqual(self.acct_line.price_subtotal, 50.0)
        res = self.acct_line._onchange_product_id()
        self.assertIn('uom_id', res['domain'])
        self.acct_line.price_unit = 100.0
        with self.assertRaises(ValidationError):
            self.contract.partner_id = False
        self.contract.partner_id = self.partner.id
        self.contract.recurring_create_invoice()
        self.invoice_monthly = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(self.invoice_monthly)
        self.assertEqual(self.contract.recurring_next_date, '2016-03-29')
        self.inv_line = self.invoice_monthly.invoice_line_ids[0]
        self.assertTrue(self.inv_line.invoice_line_tax_ids)
        self.assertAlmostEqual(self.inv_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.partner_id.user_id,
                         self.invoice_monthly.user_id)

    def test_contract_daily(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_rule_type = 'daily'
        self.contract.pricelist_id = False
        self.contract.cron_recurring_create_invoice()
        invoice_daily = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(invoice_daily)
        self.assertEqual(self.contract.recurring_next_date, '2016-03-01')

    def test_contract_weekly(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_rule_type = 'weekly'
        self.contract.recurring_invoicing_type = 'post-paid'
        self.contract.recurring_create_invoice()
        invoices_weekly = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(invoices_weekly)
        self.assertEqual(
            self.contract.recurring_next_date, '2016-03-07')

    def test_contract_yearly(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_rule_type = 'yearly'
        self.contract.recurring_create_invoice()
        invoices_weekly = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(invoices_weekly)
        self.assertEqual(
            self.contract.recurring_next_date, '2017-02-28')

    def test_contract_monthly_lastday(self):
        self.contract.recurring_next_date = '2016-02-29'
        self.contract.recurring_invoicing_type = 'post-paid'
        self.contract.recurring_rule_type = 'monthlylastday'
        self.contract.recurring_create_invoice()
        invoices_monthly_lastday = self.env['account.invoice'].search(
            [('contract_id', '=', self.contract.id)])
        self.assertTrue(invoices_monthly_lastday)
        self.assertEqual(self.contract.recurring_next_date, '2016-03-31')

    def test_recurring_when_some_raise(self):
        """A crash in multiple contracts invoice creation must not rollback
        the whole transaction.
        """

        # Generate a bunch of contracts, one half being invalid
        journal = self.env['account.journal'].search([('type', '=', 'sale')])
        journal.write({'type': 'general'})

        contracts = self.env['account.analytic.account']
        for num in range(4):
            contract = self.contract.copy()
            if num % 2:
                contract.journal_id = False
            contracts += contract

        # Generate the invoices of all contracts
        with patch.object(aaa_logger, 'exception') as mocked_log:
            invoices = contracts.recurring_create_invoice()

        # Check db state and logged errors
        count = self.env['account.invoice'].search_count(
            [('contract_id', 'in', contracts.ids)])
        self.assertEqual(count, 2)
        self.assertEqual(invoices.mapped('contract_id.id'),
                         [contracts[0].id, contracts[2].id])
        # Check there are 2 logs for each failure = traceback + custom message:
        self.assertEqual(mocked_log.call_count, 4)
        # - traceback: contains original exception name
        log_args = [args for args, kwargs in mocked_log.call_args_list]
        self.assertTrue(all('ValidationError' in l[0] for l in log_args[::2]))
        # - custom message: contains the in-failure contract identifier
        self.assertTrue(all(
            log_arg[0].startswith('Invoice creation failed for contract id %d')
            for log_arg in log_args[1::2]))
        self.assertEqual([contracts[1].id, contracts[3].id],
                         [log_arg[1] for log_arg in log_args[1::2]])

    def test_onchange_partner_id(self):
        self.contract._onchange_partner_id()
        self.assertEqual(self.contract.pricelist_id,
                         self.contract.partner_id.property_product_pricelist)

    def test_onchange_date_start(self):
        date = '2016-01-01'
        self.contract.date_start = date
        self.contract._onchange_date_start()
        self.assertEqual(self.contract.recurring_next_date, date)

    def test_uom(self):
        uom_litre = self.env.ref('product.product_uom_litre')
        self.acct_line.uom_id = uom_litre.id
        self.acct_line._onchange_product_id()
        self.assertEqual(self.acct_line.uom_id,
                         self.acct_line.product_id.uom_id)

    def test_onchange_product_id(self):
        line = self.env['account.analytic.invoice.line'].new()
        res = line._onchange_product_id()
        self.assertFalse(res['domain']['uom_id'])

    def test_no_pricelist(self):
        self.contract.pricelist_id = False
        self.acct_line.quantity = 2
        self.assertAlmostEqual(self.acct_line.price_subtotal, 100.0)

    def test_check_journal(self):
        contract_no_journal = self.contract.copy()
        contract_no_journal.journal_id = False
        journal = self.env['account.journal'].search([('type', '=', 'sale')])
        journal.write({'type': 'general'})
        with self.assertExceptionLogged(ValidationError):
            contract_no_journal.recurring_create_invoice()

    def test_check_date_end(self):
        with self.assertRaises(ValidationError):
            self.contract.date_end = '2015-12-31'

    def test_check_recurring_next_date_start_date(self):
        with self.assertRaises(ValidationError):
            self.contract.write({
                'date_start': '2017-01-01',
                'recurring_next_date': '2016-01-01',
            })

    def test_check_recurring_next_date_recurring_invoices(self):
        with self.assertRaises(ValidationError):
            self.contract.write({
                'recurring_invoices': True,
                'recurring_next_date': False,
            })

    def test_check_date_start_recurring_invoices(self):
        with self.assertRaises(ValidationError):
            self.contract.write({
                'recurring_invoices': True,
                'date_start': False,
            })

    def test_onchange_contract_template_id(self):
        """It should change the contract values to match the template."""
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        res = {
            'recurring_rule_type': self.contract.recurring_rule_type,
            'recurring_interval': self.contract.recurring_interval,
        }
        del self.template_vals['name']
        self.assertDictEqual(res, self.template_vals)

    def test_onchange_contract_template_id_lines(self):
        """It should create invoice lines for the contract lines."""

        self.acct_line.unlink()
        self.line_vals['analytic_account_id'] = self.template.id
        self.env['account.analytic.contract.line'].create(self.line_vals)
        self.contract.contract_template_id = self.template

        self.assertFalse(self.contract.recurring_invoice_line_ids,
                         'Recurring lines were not removed.')

        self.contract._onchange_contract_template_id()
        del self.line_vals['analytic_account_id']

        self.assertEqual(len(self.contract.recurring_invoice_line_ids), 1)

        for key, value in self.line_vals.items():
            test_value = self.contract.recurring_invoice_line_ids[0][key]
            try:
                test_value = test_value.id
            except AttributeError:
                pass
            self.assertEqual(test_value, value)

    def test_send_mail_contract(self):
        result = self.contract.action_contract_send()
        self.assertEqual(result['res_model'], 'mail.compose.message')

    def test_contract_onchange_product_id_domain_blank(self):
        """It should return a blank UoM domain when no product."""
        line = self.env['account.analytic.contract.line'].new()
        res = line._onchange_product_id()
        self.assertFalse(res['domain']['uom_id'])

    def test_contract_onchange_product_id_domain(self):
        """It should return UoM category domain."""
        line = self._add_template_line()
        res = line._onchange_product_id()
        self.assertEqual(
            res['domain']['uom_id'][0],
            ('category_id', '=', self.product.uom_id.category_id.id),
        )

    def test_contract_onchange_product_id_uom(self):
        """It should update the UoM for the line."""
        line = self._add_template_line(
            {'uom_id': self.env.ref('product.product_uom_litre').id}
        )
        line.product_id.uom_id = self.env.ref('product.product_uom_day').id
        line._onchange_product_id()
        self.assertEqual(line.uom_id,
                         line.product_id.uom_id)

    def test_contract_onchange_product_id_name(self):
        """It should update the name for the line."""
        line = self._add_template_line()
        line.product_id.description_sale = 'Test'
        line._onchange_product_id()
        self.assertEqual(line.name,
                         '\n'.join([line.product_id.name,
                                    line.product_id.description_sale,
                                    ]))

    def test_contract_count(self):
        """It should return contract count."""
        count = self.partner.contract_count + 2
        self.contract.copy()
        self.contract.copy()
        self.assertEqual(self.partner.contract_count, count)

    def test_same_date_start_and_date_end(self):
        """It should create one invoice with same start and end date."""
        AccountInvoice = self.env['account.invoice']
        self.contract.write({
            'date_start': fields.Date.today(),
            'date_end': fields.Date.today(),
            'recurring_next_date': fields.Date.today(),
        })
        init_count = AccountInvoice.search_count(
            [('contract_id', '=', self.contract.id)])
        self.contract.cron_recurring_create_invoice()
        last_count = AccountInvoice.search_count(
            [('contract_id', '=', self.contract.id)])
        self.assertEqual(last_count, init_count + 1)
        with self.assertExceptionLogged(ValidationError):
            self.contract.recurring_create_invoice()

    def test_compute_create_invoice_visibility(self):
        self.contract.write({
            'recurring_next_date': '2017-01-01',
            'date_start': '2016-01-01',
            'date_end': False,
        })
        self.assertTrue(self.contract.create_invoice_visibility)
        self.contract.date_end = '2017-01-01'
        self.assertTrue(self.contract.create_invoice_visibility)
        self.contract.date_end = '2016-01-01'
        self.assertFalse(self.contract.create_invoice_visibility)
