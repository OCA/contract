# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common


def to_date(date):
    return fields.Date.to_date(date)


class TestContractBase(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.pricelist = cls.env['product.pricelist'].create({
            'name': 'pricelist for contract test',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'partner test contract',
            'property_product_pricelist': cls.pricelist.id,
        })
        cls.product_1 = cls.env.ref('product.product_product_1')
        cls.product_2 = cls.env.ref('product.product_product_2')
        cls.product_1.taxes_id += cls.env['account.tax'].search(
            [('type_tax_use', '=', 'sale')], limit=1
        )
        cls.product_1.description_sale = 'Test description sale'
        cls.line_template_vals = {
            'product_id': cls.product_1.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': cls.product_1.uom_id.id,
            'price_unit': 100,
            'discount': 50,
            'recurring_rule_type': 'yearly',
            'recurring_interval': 1,
        }
        cls.template_vals = {
            'name': 'Test Contract Template',
            'contract_line_ids': [(0, 0, cls.line_template_vals)],
        }
        cls.template = cls.env['contract.template'].create(
            cls.template_vals
        )
        # For being sure of the applied price
        cls.env['product.pricelist.item'].create(
            {
                'pricelist_id': cls.partner.property_product_pricelist.id,
                'product_id': cls.product_1.id,
                'compute_price': 'formula',
                'base': 'list_price',
            }
        )
        cls.contract = cls.env['contract.contract'].create(
            {
                'name': 'Test Contract',
                'partner_id': cls.partner.id,
                'pricelist_id': cls.partner.property_product_pricelist.id,
            }
        )
        cls.contract2 = cls.env['contract.contract'].create(
            {
                'name': 'Test Contract 2',
                'partner_id': cls.partner.id,
                'pricelist_id': cls.partner.property_product_pricelist.id,
                'contract_type': 'purchase',
                'contract_line_ids': [
                    (
                        0,
                        0,
                        {
                            'product_id': cls.product_1.id,
                            'name': 'Services from #START# to #END#',
                            'quantity': 1,
                            'uom_id': cls.product_1.uom_id.id,
                            'price_unit': 100,
                            'discount': 50,
                            'recurring_rule_type': 'monthly',
                            'recurring_interval': 1,
                            'date_start': '2018-02-15',
                            'recurring_next_date': '2018-02-22',
                        },
                    )
                ],
            }
        )
        cls.line_vals = {
            'contract_id': cls.contract.id,
            'product_id': cls.product_1.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': cls.product_1.uom_id.id,
            'price_unit': 100,
            'discount': 50,
            'recurring_rule_type': 'monthly',
            'recurring_interval': 1,
            'date_start': '2018-01-01',
            'recurring_next_date': '2018-01-15',
            'is_auto_renew': False,
        }
        cls.acct_line = cls.env['contract.line'].create(
            cls.line_vals
        )
        cls.acct_line.product_id.is_auto_renew = True


class TestContract(TestContractBase):
    def _add_template_line(self, overrides=None):
        if overrides is None:
            overrides = {}
        vals = self.line_vals.copy()
        del vals['contract_id']
        del vals['date_start']
        vals['contract_id'] = self.template.id
        vals.update(overrides)
        return self.env['contract.template.line'].create(vals)

    def test_check_discount(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write({'discount': 120})

    def test_automatic_price(self):
        self.acct_line.automatic_price = True
        self.product_1.list_price = 1100
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
        recurring_next_date = to_date('2018-02-15')
        self.assertAlmostEqual(self.acct_line.price_subtotal, 50.0)
        res = self.acct_line._onchange_product_id()
        self.assertIn('uom_id', res['domain'])
        self.acct_line.price_unit = 100.0
        self.contract.partner_id = self.partner.id
        self.contract.recurring_create_invoice()
        self.invoice_monthly = self.contract._get_related_invoices()
        self.assertTrue(self.invoice_monthly)
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )
        self.inv_line = self.invoice_monthly.invoice_line_ids[0]
        self.assertTrue(self.inv_line.invoice_line_tax_ids)
        self.assertAlmostEqual(self.inv_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.user_id, self.invoice_monthly.user_id)

    def test_contract_recurring_next_date(self):
        recurring_next_date = to_date('2018-01-15')
        self.assertEqual(
            self.contract.recurring_next_date, recurring_next_date
        )
        contract_line = self.acct_line.copy(
            {'recurring_next_date': '2018-01-14'}
        )
        recurring_next_date = to_date('2018-01-14')
        self.assertEqual(
            self.contract.recurring_next_date, recurring_next_date
        )
        contract_line.cancel()
        recurring_next_date = to_date('2018-01-15')
        self.assertEqual(
            self.contract.recurring_next_date, recurring_next_date
        )

    def test_contract_daily(self):
        recurring_next_date = to_date('2018-02-23')
        last_date_invoiced = to_date('2018-02-22')
        self.acct_line.recurring_next_date = '2018-02-22'
        self.acct_line.recurring_rule_type = 'daily'
        self.contract.pricelist_id = False
        self.contract.recurring_create_invoice()
        invoice_daily = self.contract._get_related_invoices()
        self.assertTrue(invoice_daily)
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_weekly_post_paid(self):
        recurring_next_date = to_date('2018-03-01')
        last_date_invoiced = to_date('2018-02-21')
        self.acct_line.recurring_next_date = '2018-02-22'
        self.acct_line.recurring_rule_type = 'weekly'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_weekly_pre_paid(self):
        recurring_next_date = to_date('2018-03-01')
        last_date_invoiced = to_date('2018-02-28')
        self.acct_line.recurring_next_date = '2018-02-22'
        self.acct_line.recurring_rule_type = 'weekly'
        self.acct_line.recurring_invoicing_type = 'pre-paid'
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_yearly_post_paid(self):
        recurring_next_date = to_date('2019-02-22')
        last_date_invoiced = to_date('2018-02-21')
        self.acct_line.recurring_next_date = '2018-02-22'
        self.acct_line.recurring_rule_type = 'yearly'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_yearly_pre_paid(self):
        recurring_next_date = to_date('2019-02-22')
        last_date_invoiced = to_date('2019-02-21')
        self.acct_line.date_end = '2020-02-22'
        self.acct_line.recurring_next_date = '2018-02-22'
        self.acct_line.recurring_rule_type = 'yearly'
        self.acct_line.recurring_invoicing_type = 'pre-paid'
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_monthly_lastday(self):
        recurring_next_date = to_date('2018-03-31')
        last_date_invoiced = to_date('2018-02-22')
        self.acct_line.recurring_next_date = '2018-02-22'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.acct_line.recurring_rule_type = 'monthlylastday'
        self.contract.recurring_create_invoice()
        invoices_monthly_lastday = self.contract._get_related_invoices()
        self.assertTrue(invoices_monthly_lastday)
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_last_invoice_post_paid(self):
        self.acct_line.date_start = '2018-01-01'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.acct_line.date_end = '2018-03-15'
        self.acct_line._onchange_date_start()
        self.assertTrue(self.acct_line.create_invoice_visibility)
        self.assertEqual(
            self.acct_line.recurring_next_date, to_date('2018-02-01')
        )
        self.assertFalse(self.acct_line.last_date_invoiced)
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.acct_line.recurring_next_date, to_date('2018-03-01')
        )
        self.assertEqual(
            self.acct_line.last_date_invoiced, to_date('2018-01-31')
        )
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.acct_line.recurring_next_date, to_date('2018-04-01')
        )
        self.assertEqual(
            self.acct_line.last_date_invoiced, to_date('2018-02-28')
        )
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.acct_line.last_date_invoiced, to_date('2018-03-15')
        )
        self.assertFalse(self.acct_line.recurring_next_date)
        self.assertFalse(self.acct_line.create_invoice_visibility)
        invoices = self.contract._get_related_invoices()
        self.contract.recurring_create_invoice()
        new_invoices = self.contract._get_related_invoices()
        self.assertEqual(
            invoices,
            new_invoices,
            "Should not create a new invoice after the last one",
        )

    def test_last_invoice_pre_paid(self):
        self.acct_line.date_start = '2018-01-01'
        self.acct_line.recurring_invoicing_type = 'pre-paid'
        self.acct_line.date_end = '2018-03-15'
        self.acct_line._onchange_date_start()
        self.assertTrue(self.acct_line.create_invoice_visibility)
        self.assertEqual(
            self.acct_line.recurring_next_date, to_date('2018-01-01')
        )
        self.assertFalse(self.acct_line.last_date_invoiced)
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.acct_line.recurring_next_date, to_date('2018-02-01')
        )
        self.assertEqual(
            self.acct_line.last_date_invoiced, to_date('2018-01-31')
        )
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.acct_line.last_date_invoiced, to_date('2018-02-28')
        )
        self.assertEqual(
            self.acct_line.last_date_invoiced, to_date('2018-02-28')
        )
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.acct_line.last_date_invoiced, to_date('2018-03-15')
        )
        self.assertFalse(self.acct_line.recurring_next_date)
        self.assertFalse(self.acct_line.create_invoice_visibility)
        invoices = self.contract._get_related_invoices()
        self.contract.recurring_create_invoice()
        new_invoices = self.contract._get_related_invoices()
        self.assertEqual(
            invoices,
            new_invoices,
            "Should not create a new invoice after the last one",
        )

    def test_onchange_partner_id(self):
        self.contract._onchange_partner_id()
        self.assertEqual(
            self.contract.pricelist_id,
            self.contract.partner_id.property_product_pricelist,
        )

    def test_onchange_date_start(self):
        recurring_next_date = to_date('2018-01-01')
        self.acct_line.date_start = recurring_next_date
        self.acct_line._onchange_date_start()
        self.assertEqual(
            self.acct_line.recurring_next_date, recurring_next_date
        )

    def test_uom(self):
        uom_litre = self.env.ref('uom.product_uom_litre')
        self.acct_line.uom_id = uom_litre.id
        self.acct_line._onchange_product_id()
        self.assertEqual(
            self.acct_line.uom_id, self.acct_line.product_id.uom_id
        )

    def test_onchange_product_id(self):
        line = self.env['contract.line'].new()
        res = line._onchange_product_id()
        self.assertFalse(res['domain']['uom_id'])

    def test_no_pricelist(self):
        self.contract.pricelist_id = False
        self.acct_line.quantity = 2
        self.assertAlmostEqual(self.acct_line.price_subtotal, 100.0)

    def test_check_journal(self):
        journal = self.env['account.journal'].search([('type', '=', 'sale')])
        journal.write({'type': 'general'})
        with self.assertRaises(ValidationError):
            self.contract.recurring_create_invoice()

    def test_check_date_end(self):
        with self.assertRaises(ValidationError):
            self.acct_line.date_end = '2015-12-31'

    def test_check_recurring_next_date_start_date(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    'date_start': '2018-01-01',
                    'recurring_next_date': '2017-01-01',
                }
            )

    def test_onchange_contract_template_id(self):
        """It should change the contract values to match the template."""
        self.contract.contract_template_id = False
        self.contract._onchange_contract_template_id()
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        res = {
            'contract_line_ids': [
                (
                    0,
                    0,
                    {
                        'product_id': self.product_1.id,
                        'name': 'Services from #START# to #END#',
                        'quantity': 1,
                        'uom_id': self.product_1.uom_id.id,
                        'price_unit': 100,
                        'discount': 50,
                        'recurring_rule_type': 'yearly',
                        'recurring_interval': 1,
                    },
                )
            ]
        }
        del self.template_vals['name']
        self.assertDictEqual(res, self.template_vals)

    def test_onchange_contract_template_id_lines(self):
        """It should create invoice lines for the contract lines."""
        self.acct_line.cancel()
        self.acct_line.unlink()
        self.contract.contract_template_id = self.template

        self.assertFalse(
            self.contract.contract_line_ids,
            'Recurring lines were not removed.',
        )
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        self.assertEqual(len(self.contract.contract_line_ids), 1)

        for key, value in self.line_template_vals.items():
            test_value = self.contract.contract_line_ids[0][key]
            try:
                test_value = test_value.id
            except AttributeError:
                pass
            self.assertEqual(test_value, value)

    def test_send_mail_contract(self):
        result = self.contract.action_contract_send()
        self.assertEqual(result['res_model'], 'mail.compose.message')

    def test_onchange_contract_type(self):
        self.contract._onchange_contract_type()
        self.assertEqual(self.contract.journal_id.type, 'sale')
        self.assertEqual(
            self.contract.journal_id.company_id, self.contract.company_id
        )
        self.contract.type = 'purchase'
        self.contract._onchange_contract_type()
        self.assertFalse(
            any(
                self.contract.contract_line_ids.mapped(
                    'automatic_price'
                )
            )
        )

    def test_contract_onchange_product_id_domain_blank(self):
        """It should return a blank UoM domain when no product."""
        line = self.env['contract.template.line'].new()
        res = line._onchange_product_id()
        self.assertFalse(res['domain']['uom_id'])

    def test_contract_onchange_product_id_domain(self):
        """It should return UoM category domain."""
        line = self._add_template_line()
        res = line._onchange_product_id()
        self.assertEqual(
            res['domain']['uom_id'][0],
            ('category_id', '=', self.product_1.uom_id.category_id.id),
        )

    def test_contract_onchange_product_id_uom(self):
        """It should update the UoM for the line."""
        line = self._add_template_line(
            {'uom_id': self.env.ref('uom.product_uom_litre').id}
        )
        line.product_id.uom_id = self.env.ref('uom.product_uom_day').id
        line._onchange_product_id()
        self.assertEqual(line.uom_id, line.product_id.uom_id)

    def test_contract_onchange_product_id_name(self):
        """It should update the name for the line."""
        line = self._add_template_line()
        line.product_id.description_sale = 'Test'
        line._onchange_product_id()
        self.assertEqual(
            line.name, line.product_id.get_product_multiline_description_sale()
        )

    def test_contract_count(self):
        """It should return sale contract count."""
        sale_count = self.partner.sale_contract_count + 2
        self.contract.copy()
        self.contract.copy()
        purchase_count = self.partner.purchase_contract_count + 1
        self.contract2.copy()
        self.partner.refresh()
        self.assertEqual(self.partner.sale_contract_count, sale_count)
        self.assertEqual(self.partner.purchase_contract_count, purchase_count)

    def test_same_date_start_and_date_end(self):
        """It should create one invoice with same start and end date."""
        self.acct_line.write(
            {
                'date_start': self.today,
                'date_end': self.today,
                'recurring_next_date': self.today,
            }
        )
        self.contract._compute_recurring_next_date()
        init_count = len(self.contract._get_related_invoices())
        self.contract.recurring_create_invoice()
        last_count = len(self.contract._get_related_invoices())
        self.assertEqual(last_count, init_count + 1)
        self.contract.recurring_create_invoice()
        last_count = len(self.contract._get_related_invoices())
        self.assertEqual(last_count, init_count + 1)

    def test_act_show_contract(self):
        show_contract = self.partner.with_context(
            contract_type='sale'
        ).act_show_contract()
        self.assertDictContainsSubset(
            {
                'name': 'Customer Contracts',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'res_model': 'contract.contract',
                'xml_id': 'contract.action_customer_contract',
            },
            show_contract,
            'There was an error and the view couldn\'t be opened.',
        )

    def test_compute_first_recurring_next_date(self):
        """Test different combination to compute recurring_next_date
        Combination format
        {
            'recurring_next_date': (      # date
                date_start,               # date
                recurring_invoicing_type, # ('pre-paid','post-paid',)
                recurring_rule_type,      # ('daily', 'weekly', 'monthly',
                                          #  'monthlylastday', 'yearly'),
                recurring_interval,       # integer
            ),
        }
        """

        def error_message(
            date_start,
            recurring_invoicing_type,
            recurring_rule_type,
            recurring_interval,
        ):
            return "Error in %s every %d %s case, start with %s " % (
                recurring_invoicing_type,
                recurring_interval,
                recurring_rule_type,
                date_start,
            )

        combinations = [
            (
                to_date('2018-01-01'),
                (to_date('2018-01-01'), 'pre-paid', 'monthly', 1),
            ),
            (
                to_date('2018-01-01'),
                (to_date('2018-01-01'), 'pre-paid', 'monthly', 2),
            ),
            (
                to_date('2018-02-01'),
                (to_date('2018-01-01'), 'post-paid', 'monthly', 1),
            ),
            (
                to_date('2018-03-01'),
                (to_date('2018-01-01'), 'post-paid', 'monthly', 2),
            ),
            (
                to_date('2018-01-31'),
                (to_date('2018-01-05'), 'post-paid', 'monthlylastday', 1),
            ),
            (
                to_date('2018-01-31'),
                (to_date('2018-01-06'), 'pre-paid', 'monthlylastday', 1),
            ),
            (
                to_date('2018-02-28'),
                (to_date('2018-01-05'), 'pre-paid', 'monthlylastday', 2),
            ),
            (
                to_date('2018-01-05'),
                (to_date('2018-01-05'), 'pre-paid', 'yearly', 1),
            ),
            (
                to_date('2019-01-05'),
                (to_date('2018-01-05'), 'post-paid', 'yearly', 1),
            ),
        ]
        contract_line_env = self.env['contract.line']
        for recurring_next_date, combination in combinations:
            self.assertEqual(
                recurring_next_date,
                contract_line_env._compute_first_recurring_next_date(
                    *combination
                ),
                error_message(*combination),
            )

    def test_recurring_next_date(self):
        """recurring next date for a contract is the min for all lines"""
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.contract.recurring_next_date,
            min(
                self.contract.contract_line_ids.mapped(
                    'recurring_next_date'
                )
            ),
        )

    def test_date_end(self):
        """recurring next date for a contract is the min for all lines"""
        self.acct_line.date_end = '2018-01-01'
        self.acct_line.copy()
        self.acct_line.write({'date_end': False, 'is_auto_renew': False})
        self.assertFalse(self.contract.date_end)

    def test_stop_contract_line(self):
        """It should raise a validation error"""
        self.acct_line.cancel()
        with self.assertRaises(ValidationError):
            self.acct_line.stop(self.today)

    def test_stop_contract_line(self):
        """It should put end to the contract line"""
        self.acct_line.write(
            {
                'date_start': self.today,
                'recurring_next_date': self.today,
                'date_end': self.today + relativedelta(months=7),
                'is_auto_renew': True,
            }
        )
        self.acct_line.stop(self.today + relativedelta(months=5))
        self.assertEqual(
            self.acct_line.date_end, self.today + relativedelta(months=5)
        )

    def test_stop_upcoming_contract_line(self):
        """It should put end to the contract line"""
        self.acct_line.write(
            {
                'date_start': self.today + relativedelta(months=3),
                'recurring_next_date': self.today + relativedelta(months=3),
                'date_end': self.today + relativedelta(months=7),
                'is_auto_renew': True,
            }
        )
        self.acct_line.stop(self.today)
        self.assertEqual(
            self.acct_line.date_end, self.today + relativedelta(months=7)
        )
        self.assertTrue(self.acct_line.is_canceled)

    def test_stop_past_contract_line(self):
        """Past contract line are ignored on stop"""
        self.acct_line.write(
            {
                'date_end': self.today + relativedelta(months=5),
                'is_auto_renew': True,
            }
        )
        self.acct_line.stop(self.today + relativedelta(months=7))
        self.assertEqual(
            self.acct_line.date_end, self.today + relativedelta(months=5)
        )

    def test_stop_contract_line_without_date_end(self):
        """Past contract line are ignored on stop"""
        self.acct_line.write({'date_end': False, 'is_auto_renew': False})
        self.acct_line.stop(self.today + relativedelta(months=7))
        self.assertEqual(
            self.acct_line.date_end, self.today + relativedelta(months=7)
        )

    def test_stop_wizard(self):
        self.acct_line.write(
            {
                'date_start': self.today,
                'recurring_next_date': self.today,
                'date_end': self.today + relativedelta(months=5),
                'is_auto_renew': True,
            }
        )
        wizard = self.env['contract.line.wizard'].create(
            {
                'date_end': self.today + relativedelta(months=3),
                'contract_line_id': self.acct_line.id,
            }
        )
        wizard.stop()
        self.assertEqual(
            self.acct_line.date_end, self.today + relativedelta(months=3)
        )
        self.assertFalse(self.acct_line.is_auto_renew)

    def test_stop_plan_successor_contract_line_0(self):
        successor_contract_line = self.acct_line.copy(
            {
                'date_start': self.today + relativedelta(months=5),
                'recurring_next_date': self.today + relativedelta(months=5),
            }
        )
        self.acct_line.write(
            {
                'successor_contract_line_id': successor_contract_line.id,
                'is_auto_renew': False,
                'date_end': self.today,
            }
        )
        suspension_start = self.today + relativedelta(months=5)
        suspension_end = self.today + relativedelta(months=6)
        with self.assertRaises(ValidationError):
            self.acct_line.stop_plan_successor(
                suspension_start, suspension_end, True
            )

    def test_stop_plan_successor_contract_line_1(self):
        """
        * contract line end's before the suspension period:
                -> apply stop
        """
        suspension_start = self.today + relativedelta(months=5)
        suspension_end = self.today + relativedelta(months=6)
        start_date = self.today
        end_date = self.today + relativedelta(months=4)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(self.acct_line.date_end, end_date)
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_stop_plan_successor_contract_line_2(self):
        """
        * contract line start before the suspension period and end in it
                -> apply stop at suspension start date
                -> apply plan successor:
                    - date_start: suspension.date_end
                    - date_end: suspension.date_end + (contract_line.date_end
                                                    - suspension.date_start)
        """
        suspension_start = self.today + relativedelta(months=3)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today
        end_date = self.today + relativedelta(months=4)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertTrue(new_line)
        new_date_end = (
            suspension_end
            + (end_date - suspension_start)
            + relativedelta(days=1)
        )
        self.assertEqual(
            new_line.date_start, suspension_end + relativedelta(days=1)
        )
        self.assertEqual(new_line.date_end, new_date_end)
        self.assertTrue(self.acct_line.manual_renew_needed)

    def test_stop_plan_successor_contract_line_3(self):
        """
        * contract line start before the suspension period and end after it
                -> apply stop at suspension start date
                -> apply plan successor:
                    - date_start: suspension.date_end
                    - date_end: suspension.date_end + (suspension.date_end
                                                    - suspension.date_start)
        """
        suspension_start = self.today + relativedelta(months=3)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today
        end_date = self.today + relativedelta(months=6)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertTrue(new_line)
        new_date_end = (
            end_date
            + (suspension_end - suspension_start)
            + relativedelta(days=1)
        )
        self.assertEqual(
            new_line.date_start, suspension_end + relativedelta(days=1)
        )
        self.assertEqual(new_line.date_end, new_date_end)
        self.assertTrue(self.acct_line.manual_renew_needed)

    def test_stop_plan_successor_contract_line_3_without_end_date(self):
        """
        * contract line start before the suspension period and end after it
                -> apply stop at suspension start date
                -> apply plan successor:
                    - date_start: suspension.date_end
                    - date_end: suspension.date_end + (suspension.date_end
                                                    - suspension.date_start)
        """
        suspension_start = self.today + relativedelta(months=3)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today
        end_date = False
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
                'is_auto_renew': False,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, False
        )
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertTrue(new_line)
        self.assertEqual(
            new_line.date_start, suspension_end + relativedelta(days=1)
        )
        self.assertFalse(new_line.date_end)
        self.assertTrue(self.acct_line.manual_renew_needed)

    def test_stop_plan_successor_contract_line_4(self):
        """
        * contract line start and end's in the suspension period
                -> apply delay
                    - delay: suspension.date_end - contract_line.end_date
        """
        suspension_start = self.today + relativedelta(months=2)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today + relativedelta(months=3)
        end_date = self.today + relativedelta(months=4)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - start_date) + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - start_date) + timedelta(days=1),
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_stop_plan_successor_contract_line_5(self):
        """
        * contract line start in the suspension period and end after it
                -> apply delay
                    - delay: suspension.date_end - contract_line.date_start
        """
        suspension_start = self.today + relativedelta(months=2)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today + relativedelta(months=3)
        end_date = self.today + relativedelta(months=6)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - start_date) + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - start_date) + timedelta(days=1),
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_stop_plan_successor_contract_line_5_without_date_end(self):
        """
        * contract line start in the suspension period and end after it
                -> apply delay
                    - delay: suspension.date_end - contract_line.date_start
        """
        suspension_start = self.today + relativedelta(months=2)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today + relativedelta(months=3)
        end_date = False
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
                'is_auto_renew': False,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - start_date) + timedelta(days=1),
        )
        self.assertFalse(self.acct_line.date_end)
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_stop_plan_successor_contract_line_6(self):
        """
        * contract line start  and end after the suspension period
                -> apply delay
                    - delay: suspension.date_end - suspension.start_date
        """
        suspension_start = self.today + relativedelta(months=2)
        suspension_end = self.today + relativedelta(months=3)
        start_date = self.today + relativedelta(months=4)
        end_date = self.today + relativedelta(months=6)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_start,
            start_date
            + (suspension_end - suspension_start)
            + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - suspension_start) + timedelta(days=1),
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_stop_plan_successor_contract_line_6_without_date_end(self):
        """
        * contract line start  and end after the suspension period
                -> apply delay
                    - delay: suspension.date_end - suspension.start_date
        """
        suspension_start = self.today + relativedelta(months=2)
        suspension_end = self.today + relativedelta(months=3)
        start_date = self.today + relativedelta(months=4)
        end_date = False
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
                'is_auto_renew': False,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_start,
            start_date
            + (suspension_end - suspension_start)
            + timedelta(days=1),
        )
        self.assertFalse(self.acct_line.date_end)
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_stop_plan_successor_wizard(self):
        suspension_start = self.today + relativedelta(months=2)
        suspension_end = self.today + relativedelta(months=3)
        start_date = self.today + relativedelta(months=4)
        end_date = self.today + relativedelta(months=6)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        wizard = self.env['contract.line.wizard'].create(
            {
                'date_start': suspension_start,
                'date_end': suspension_end,
                'is_auto_renew': False,
                'contract_line_id': self.acct_line.id,
            }
        )
        wizard.stop_plan_successor()
        self.assertEqual(
            self.acct_line.date_start,
            start_date
            + (suspension_end - suspension_start)
            + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - suspension_start) + timedelta(days=1),
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_plan_successor_contract_line(self):
        self.acct_line.write(
            {
                'date_start': self.today,
                'recurring_next_date': self.today,
                'date_end': self.today + relativedelta(months=3),
                'is_auto_renew': False,
            }
        )
        self.acct_line.plan_successor(
            self.today + relativedelta(months=5),
            self.today + relativedelta(months=7),
            True,
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(self.acct_line.is_auto_renew)
        self.assertTrue(new_line.is_auto_renew)
        self.assertTrue(new_line, "should create a new contract line")
        self.assertEqual(
            new_line.date_start, self.today + relativedelta(months=5)
        )
        self.assertEqual(
            new_line.date_end, self.today + relativedelta(months=7)
        )

    def test_overlap(self):
        self.acct_line.write(
            {
                'date_start': self.today,
                'recurring_next_date': self.today,
                'date_end': self.today + relativedelta(months=3),
                'is_auto_renew': False,
            }
        )
        self.acct_line.plan_successor(
            self.today + relativedelta(months=5),
            self.today + relativedelta(months=7),
            True,
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        with self.assertRaises(ValidationError):
            new_line.date_start = self.today + relativedelta(months=2)
        with self.assertRaises(ValidationError):
            self.acct_line.date_end = self.today + relativedelta(months=6)

    def test_plan_successor_wizard(self):
        self.acct_line.write(
            {
                'date_start': self.today,
                'recurring_next_date': self.today,
                'date_end': self.today + relativedelta(months=2),
                'is_auto_renew': False,
            }
        )
        wizard = self.env['contract.line.wizard'].create(
            {
                'date_start': self.today + relativedelta(months=3),
                'date_end': self.today + relativedelta(months=5),
                'is_auto_renew': True,
                'contract_line_id': self.acct_line.id,
            }
        )
        wizard.plan_successor()
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertFalse(self.acct_line.is_auto_renew)
        self.assertTrue(new_line.is_auto_renew)
        self.assertTrue(new_line, "should create a new contract line")
        self.assertEqual(
            new_line.date_start, self.today + relativedelta(months=3)
        )
        self.assertEqual(
            new_line.date_end, self.today + relativedelta(months=5)
        )

    def test_cancel(self):
        self.acct_line.write(
            {
                'date_end': self.today + relativedelta(months=5),
                'is_auto_renew': True,
            }
        )
        self.acct_line.cancel()
        self.assertTrue(self.acct_line.is_canceled)
        self.assertFalse(self.acct_line.is_auto_renew)
        with self.assertRaises(ValidationError):
            self.acct_line.is_auto_renew = True
        self.acct_line.uncancel(self.today)
        self.assertFalse(self.acct_line.is_canceled)

    def test_uncancel_wizard(self):
        self.acct_line.cancel()
        self.assertTrue(self.acct_line.is_canceled)
        wizard = self.env['contract.line.wizard'].create(
            {
                'recurring_next_date': self.today,
                'contract_line_id': self.acct_line.id,
            }
        )
        wizard.uncancel()
        self.assertFalse(self.acct_line.is_canceled)

    def test_cancel_uncancel_with_predecessor(self):
        suspension_start = self.today + relativedelta(months=3)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today
        end_date = self.today + relativedelta(months=4)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        self.assertEqual(self.acct_line.successor_contract_line_id, new_line)
        new_line.cancel()
        self.assertTrue(new_line.is_canceled)
        self.assertFalse(self.acct_line.successor_contract_line_id)
        self.assertEqual(new_line.predecessor_contract_line_id, self.acct_line)
        new_line.uncancel(suspension_end + relativedelta(days=1))
        self.assertFalse(new_line.is_canceled)
        self.assertEqual(self.acct_line.successor_contract_line_id, new_line)
        self.assertEqual(
            new_line.recurring_next_date,
            suspension_end + relativedelta(days=1),
        )

    def test_cancel_uncancel_with_predecessor_has_successor(self):
        suspension_start = self.today + relativedelta(months=6)
        suspension_end = self.today + relativedelta(months=7)
        start_date = self.today
        end_date = self.today + relativedelta(months=8)
        self.acct_line.write(
            {
                'date_start': start_date,
                'recurring_next_date': start_date,
                'date_end': end_date,
            }
        )
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        new_line = self.env['contract.line'].search(
            [('predecessor_contract_line_id', '=', self.acct_line.id)]
        )
        new_line.cancel()
        suspension_start = self.today + relativedelta(months=4)
        suspension_end = self.today + relativedelta(months=5)
        self.acct_line.stop_plan_successor(
            suspension_start, suspension_end, True
        )
        with self.assertRaises(ValidationError):
            new_line.uncancel(suspension_end)

    def test_check_has_not_date_end_has_successor(self):
        self.acct_line.write({'date_end': False, 'is_auto_renew': False})
        with self.assertRaises(ValidationError):
            self.acct_line.plan_successor(
                to_date('2016-03-01'), to_date('2016-09-01'), False
            )

    def test_check_has_not_date_end_is_auto_renew(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write({'date_end': False, 'is_auto_renew': True})

    def test_check_has_successor_is_auto_renew(self):
        with self.assertRaises(ValidationError):
            self.acct_line.plan_successor(
                to_date('2016-03-01'), to_date('2018-09-01'), False
            )

    def test_search_contract_line_to_renew(self):
        self.acct_line.write({'date_end': self.today, 'is_auto_renew': True})
        line_1 = self.acct_line.copy(
            {'date_end': self.today + relativedelta(months=1)}
        )
        line_2 = self.acct_line.copy(
            {'date_end': self.today - relativedelta(months=1)}
        )
        line_3 = self.acct_line.copy(
            {'date_end': self.today - relativedelta(months=2)}
        )
        line_4 = self.acct_line.copy(
            {'date_end': self.today + relativedelta(months=2)}
        )
        to_renew = self.acct_line.search(
            self.acct_line._contract_line_to_renew_domain()
        )
        self.assertEqual(
            set(to_renew), set((self.acct_line, line_1, line_2, line_3))
        )
        self.acct_line.cron_renew_contract_line()
        self.assertTrue(self.acct_line.successor_contract_line_id)
        self.assertTrue(line_1.successor_contract_line_id)
        self.assertTrue(line_2.successor_contract_line_id)
        self.assertTrue(line_3.successor_contract_line_id)
        self.assertFalse(line_4.successor_contract_line_id)

    def test_renew(self):
        date_start = self.today - relativedelta(months=9)
        date_end = (
            date_start + relativedelta(months=12) - relativedelta(days=1)
        )
        self.acct_line.write(
            {
                'is_auto_renew': True,
                'date_start': date_start,
                'recurring_next_date': date_start,
                'date_end': self.today,
            }
        )
        self.acct_line._onchange_is_auto_renew()
        self.assertEqual(self.acct_line.date_end, date_end)
        new_line = self.acct_line.renew()
        self.assertFalse(self.acct_line.is_auto_renew)
        self.assertTrue(new_line.is_auto_renew)
        self.assertEqual(
            new_line.date_start, date_start + relativedelta(months=12)
        )
        self.assertEqual(
            new_line.date_end, date_end + relativedelta(months=12)
        )

    def test_cron_recurring_create_invoice(self):
        self.acct_line.date_start = '2018-01-01'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.acct_line.date_end = '2018-03-15'
        self.acct_line._onchange_date_start()
        contracts = self.contract2
        for i in range(10):
            contracts |= self.contract.copy()
        self.env['contract.contract'].cron_recurring_create_invoice()
        invoice_lines = self.env['account.invoice.line'].search(
            [('contract_line_id', 'in',
              contracts.mapped('contract_line_ids').ids)]
        )
        self.assertEqual(
            len(contracts.mapped('contract_line_ids')),
            len(invoice_lines),
        )

    def test_get_period_to_invoice_monthlylastday(self):
        self.acct_line.date_start = '2018-01-05'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.acct_line.recurring_rule_type = 'monthlylastday'
        self.acct_line.date_end = '2018-03-15'
        self.acct_line._onchange_date_start()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-01-05'))
        self.assertEqual(last, to_date('2018-01-31'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-02-01'))
        self.assertEqual(last, to_date('2018-02-28'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-03-01'))
        self.assertEqual(last, to_date('2018-03-15'))
        self.acct_line.manual_renew_needed = True

    def test_get_period_to_invoice_monthly_pre_paid_2(self):
        self.acct_line.date_start = '2018-01-05'
        self.acct_line.recurring_invoicing_type = 'pre-paid'
        self.acct_line.recurring_rule_type = 'monthly'
        self.acct_line.date_end = '2018-08-15'
        self.acct_line._onchange_date_start()
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-02-05'))
        self.assertEqual(last, to_date('2018-03-04'))
        self.acct_line.recurring_next_date = '2018-06-05'
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-02-05'))
        self.assertEqual(last, to_date('2018-07-04'))

    def test_get_period_to_invoice_monthly_post_paid_2(self):
        self.acct_line.date_start = '2018-01-05'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.acct_line.recurring_rule_type = 'monthly'
        self.acct_line.date_end = '2018-08-15'
        self.acct_line._onchange_date_start()
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-02-05'))
        self.assertEqual(last, to_date('2018-03-04'))
        self.acct_line.recurring_next_date = '2018-06-05'
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-02-05'))
        self.assertEqual(last, to_date('2018-06-04'))

    def test_get_period_to_invoice_monthly_post_paid(self):
        self.acct_line.date_start = '2018-01-05'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.acct_line.recurring_rule_type = 'monthly'
        self.acct_line.date_end = '2018-03-15'
        self.acct_line._onchange_date_start()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-01-05'))
        self.assertEqual(last, to_date('2018-02-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-02-05'))
        self.assertEqual(last, to_date('2018-03-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-03-05'))
        self.assertEqual(last, to_date('2018-03-15'))

    def test_get_period_to_invoice_monthly_pre_paid(self):
        self.acct_line.date_start = '2018-01-05'
        self.acct_line.recurring_invoicing_type = 'pre-paid'
        self.acct_line.recurring_rule_type = 'monthly'
        self.acct_line.date_end = '2018-03-15'
        self.acct_line._onchange_date_start()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-01-05'))
        self.assertEqual(last, to_date('2018-02-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-02-05'))
        self.assertEqual(last, to_date('2018-03-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-03-05'))
        self.assertEqual(last, to_date('2018-03-15'))

    def test_get_period_to_invoice_yearly_post_paid(self):
        self.acct_line.date_start = '2018-01-05'
        self.acct_line.recurring_invoicing_type = 'post-paid'
        self.acct_line.recurring_rule_type = 'yearly'
        self.acct_line.date_end = '2020-03-15'
        self.acct_line._onchange_date_start()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-01-05'))
        self.assertEqual(last, to_date('2019-01-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2019-01-05'))
        self.assertEqual(last, to_date('2020-01-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2020-01-05'))
        self.assertEqual(last, to_date('2020-03-15'))

    def test_get_period_to_invoice_yearly_pre_paid(self):
        self.acct_line.date_start = '2018-01-05'
        self.acct_line.recurring_invoicing_type = 'pre-paid'
        self.acct_line.recurring_rule_type = 'yearly'
        self.acct_line.date_end = '2020-03-15'
        self.acct_line._onchange_date_start()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2018-01-05'))
        self.assertEqual(last, to_date('2019-01-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2019-01-05'))
        self.assertEqual(last, to_date('2020-01-04'))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = \
            self.acct_line._get_period_to_invoice(
                self.acct_line.last_date_invoiced,
                self.acct_line.recurring_next_date,
            )
        self.assertEqual(first, to_date('2020-01-05'))
        self.assertEqual(last, to_date('2020-03-15'))

    def test_unlink(self):
        with self.assertRaises(ValidationError):
            self.acct_line.unlink()

    def test_contract_line_state(self):
        lines = self.env['contract.line']
        # upcoming
        lines |= self.acct_line.copy(
            {
                'date_start': self.today + relativedelta(months=3),
                'recurring_next_date': self.today + relativedelta(months=3),
                'date_end': self.today + relativedelta(months=5),
            }
        )
        # in-progress
        lines |= self.acct_line.copy(
            {
                'date_start': self.today,
                'recurring_next_date': self.today,
                'date_end': self.today + relativedelta(months=5),
            }
        )
        # in-progress
        lines |= self.acct_line.copy(
            {
                'date_start': self.today,
                'recurring_next_date': self.today,
                'date_end': self.today + relativedelta(months=5),
                'manual_renew_needed': True,
            }
        )
        # to-renew
        lines |= self.acct_line.copy(
            {
                'date_start': self.today - relativedelta(months=5),
                'recurring_next_date': self.today - relativedelta(months=5),
                'date_end': self.today - relativedelta(months=2),
                'manual_renew_needed': True,
            }
        )
        # upcoming-close
        lines |= self.acct_line.copy(
            {
                'date_start': self.today - relativedelta(months=5),
                'recurring_next_date': self.today - relativedelta(months=5),
                'date_end': self.today + relativedelta(days=20),
                'is_auto_renew': False,
            }
        )
        # closed
        lines |= self.acct_line.copy(
            {
                'date_start': self.today - relativedelta(months=5),
                'recurring_next_date': self.today - relativedelta(months=5),
                'date_end': self.today - relativedelta(months=2),
                'is_auto_renew': False,
            }
        )
        # canceled
        lines |= self.acct_line.copy(
            {
                'date_start': self.today - relativedelta(months=5),
                'recurring_next_date': self.today - relativedelta(months=5),
                'date_end': self.today - relativedelta(months=2),
                'is_canceled': True,
            }
        )
        states = [
            'upcoming',
            'in-progress',
            'to-renew',
            'upcoming-close',
            'closed',
            'canceled',
        ]
        self.assertEqual(set(lines.mapped('state')), set(states))
        for state in states:
            lines = self.env['contract.line'].search(
                [('state', '=', state)]
            )
            self.assertEqual(len(set(lines.mapped('state'))), 1, state)
            self.assertEqual(lines.mapped('state')[0], state, state)

        for state in states:
            lines = self.env['contract.line'].search(
                [('state', '!=', state)]
            )
            self.assertFalse(state in lines.mapped('state'))

        lines = self.env['contract.line'].search(
            [('state', 'in', states)]
        )
        self.assertEqual(set(lines.mapped('state')), set(states))
        lines = self.env['contract.line'].search(
            [('state', 'in', [])]
        )
        self.assertFalse(lines.mapped('state'))
        with self.assertRaises(TypeError):
            self.env['contract.line'].search(
                [('state', 'in', 'upcoming')]
            )
        lines = self.env['contract.line'].search(
            [('state', 'not in', [])]
        )
        self.assertEqual(set(lines.mapped('state')), set(states))
        lines = self.env['contract.line'].search(
            [('state', 'not in', states)]
        )
        self.assertFalse(lines.mapped('state'))
        lines = self.env['contract.line'].search(
            [('state', 'not in', ['upcoming', 'in-progress'])]
        )
        self.assertEqual(
            set(lines.mapped('state')),
            set(['to-renew', 'upcoming-close', 'closed', 'canceled']),
        )

    def test_check_auto_renew_contract_line_with_successor(self):
        """
        A contract line with a successor can't be set to auto-renew
        """
        successor_contract_line = self.acct_line.copy()
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    'is_auto_renew': True,
                    'successor_contract_line_id': successor_contract_line.id,
                }
            )

    def test_check_no_date_end_contract_line_with_successor(self):
        """
        A contract line with a successor must have a end date
        """
        successor_contract_line = self.acct_line.copy()
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    'date_end': False,
                    'successor_contract_line_id': successor_contract_line.id,
                }
            )

    def test_check_last_date_invoiced_1(self):
        """
        start end can't be before the date of last invoice
        """
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    'last_date_invoiced': self.acct_line.date_start
                    - relativedelta(days=1)
                }
            )

    def test_check_last_date_invoiced_2(self):
        """
        start date can't be after the date of last invoice
        """
        self.acct_line.write({'date_end': self.today})
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    'last_date_invoiced': self.acct_line.date_end
                    + relativedelta(days=1)
                }
            )

    def test_init_last_date_invoiced(self):
        self.acct_line.write(
            {'date_start': '2019-01-01', 'recurring_next_date': '2019-03-01'}
        )
        line_monthlylastday = self.acct_line.copy(
            {
                'recurring_rule_type': 'monthlylastday',
                'recurring_next_date': '2019-03-31',
            }
        )
        line_prepaid = self.acct_line.copy(
            {
                'recurring_invoicing_type': 'pre-paid',
                'recurring_rule_type': 'monthly',
            }
        )
        line_postpaid = self.acct_line.copy(
            {
                'recurring_invoicing_type': 'post-paid',
                'recurring_rule_type': 'monthly',
            }
        )
        lines = line_monthlylastday | line_prepaid | line_postpaid
        lines.write({'last_date_invoiced': False})
        self.assertFalse(any(lines.mapped('last_date_invoiced')))
        lines._init_last_date_invoiced()
        self.assertEqual(
            line_monthlylastday.last_date_invoiced, to_date("2019-02-28")
        )
        self.assertEqual(
            line_prepaid.last_date_invoiced, to_date("2019-02-28")
        )
        self.assertEqual(
            line_postpaid.last_date_invoiced, to_date("2019-01-31")
        )

    def test_delay_invoiced_contract_line(self):
        self.acct_line.write(
            {
                'last_date_invoiced': self.acct_line.date_start
                + relativedelta(days=1)
            }
        )
        with self.assertRaises(ValidationError):
            self.acct_line._delay(relativedelta(months=1))

    def test_cancel_invoiced_contract_line(self):
        self.acct_line.write(
            {
                'last_date_invoiced': self.acct_line.date_start
                + relativedelta(days=1)
            }
        )
        with self.assertRaises(ValidationError):
            self.acct_line.cancel()

    def test_action_uncancel(self):
        action = self.acct_line.action_uncancel()
        self.assertEqual(
            action['context']['default_contract_line_id'], self.acct_line.id
        )

    def test_action_plan_successor(self):
        action = self.acct_line.action_plan_successor()
        self.assertEqual(
            action['context']['default_contract_line_id'], self.acct_line.id
        )

    def test_action_stop(self):
        action = self.acct_line.action_stop()
        self.assertEqual(
            action['context']['default_contract_line_id'], self.acct_line.id
        )

    def test_action_stop_plan_successor(self):
        action = self.acct_line.action_stop_plan_successor()
        self.assertEqual(
            action['context']['default_contract_line_id'], self.acct_line.id
        )

    def test_purchase_fields_view_get(self):
        purchase_tree_view = self.env.ref(
            'contract.contract_line_supplier_tree_view'
        )
        purchase_form_view = self.env.ref(
            'contract.contract_line_supplier_form_view'
        )
        view = self.acct_line.with_context(
            default_contract_type='purchase'
        ).fields_view_get(view_type='tree')
        self.assertEqual(view['view_id'], purchase_tree_view.id)
        view = self.acct_line.with_context(
            default_contract_type='purchase'
        ).fields_view_get(view_type='form')
        self.assertEqual(view['view_id'], purchase_form_view.id)

    def test_sale_fields_view_get(self):
        sale_form_view = self.env.ref(
            'contract.contract_line_customer_form_view'
        )
        view = self.acct_line.with_context(
            default_contract_type='sale'
        ).fields_view_get(view_type='form')
        self.assertEqual(view['view_id'], sale_form_view.id)

    def test_contract_count_invoice(self):
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.contract._compute_invoice_count()
        self.assertEqual(self.contract.invoice_count, 3)

    def test_contract_count_invoice(self):
        invoices = self.env['account.invoice']
        invoices |= self.contract.recurring_create_invoice()
        invoices |= self.contract.recurring_create_invoice()
        invoices |= self.contract.recurring_create_invoice()
        action = self.contract.action_show_invoices()
        self.assertEqual(set(action['domain'][0][2]), set(invoices.ids))

    def test_compute_create_invoice_visibility(self):
        self.assertTrue(self.contract.create_invoice_visibility)
        self.acct_line.write(
            {
                'date_start': '2018-01-01',
                'date_end': '2018-12-31',
                'last_date_invoiced': '2018-12-31',
                'recurring_next_date': False,
            }
        )
        self.assertFalse(self.acct_line.create_invoice_visibility)
        self.assertFalse(self.contract.create_invoice_visibility)

    def test_invoice_contract_without_lines(self):
        self.contract.contract_line_ids.cancel()
        self.contract.contract_line_ids.unlink()
        self.assertFalse(self.contract.recurring_create_invoice())

    def test_stop_at_last_date_invoiced(self):
        self.contract.recurring_create_invoice()
        self.assertTrue(self.acct_line.recurring_next_date)
        self.acct_line.stop(self.acct_line.last_date_invoiced)
        self.assertFalse(self.acct_line.recurring_next_date)
