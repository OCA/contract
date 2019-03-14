# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo.addons.contract.tests.test_contract import TestContractBase
from odoo.fields import Date
from odoo.tools import mute_logger


class TestContractLineForecastPeriod(TestContractBase):
    @mute_logger("odoo.addons.queue_job.models.base")
    def setUp(self):
        self.env = self.env(
            context=dict(self.env.context, test_queue_job_no_delay=True)
        )
        super(TestContractLineForecastPeriod, self).setUp()
        self.line_vals["date_start"] = Date.context_today(self.acct_line)
        self.line_vals["recurring_next_date"] = Date.context_today(
            self.acct_line
        )
        self.acct_line = self.env["account.analytic.invoice.line"].create(
            self.line_vals
        )

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_creation(self):
        self.acct_line.write(
            {
                'date_start': "2019-01-01",
                'recurring_next_date': "2019-01-01",
                'date_end': "2019-12-31",
                'recurring_rule_type': "monthly",
                'recurring_invoicing_type': 'pre-paid',
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 12)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_1(self):
        self.acct_line.write(
            {
                'date_start': "2019-01-01",
                'recurring_next_date': "2019-01-01",
                'date_end': "2019-12-31",
                'recurring_rule_type': "yearly",
                'recurring_invoicing_type': 'pre-paid',
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_2(self):
        self.acct_line.write(
            {
                'date_start': "2019-01-01",
                'recurring_next_date': "2019-01-31",
                'date_end': "2019-6-05",
                'recurring_rule_type': "monthlylastday",
                'recurring_invoicing_type': 'pre-paid',
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 6)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_3(self):
        self.assertEqual(self.acct_line.price_subtotal, 50)
        self.acct_line.write({"price_unit": 50})
        self.assertEqual(self.acct_line.price_subtotal, 25)
        self.assertEqual(
            self.acct_line.forecast_period_ids[0].price_subtotal, 25
        )

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_4(self):
        self.assertEqual(self.acct_line.price_subtotal, 50)
        self.acct_line.write({"discount": 0})
        self.assertEqual(self.acct_line.price_subtotal, 100)
        self.assertEqual(
            self.acct_line.forecast_period_ids[0].price_subtotal, 100
        )

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_5(self):
        self.acct_line.cancel()
        self.assertFalse(self.acct_line.forecast_period_ids)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_6(self):
        self.acct_line.write(
            {
                'date_start': "2019-01-01",
                'recurring_next_date': "2019-01-01",
                'date_end': "2019-01-28",
                'recurring_rule_type': "monthly",
                'recurring_invoicing_type': 'pre-paid',
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_6(self):
        self.acct_line.write(
            {
                'date_start': "2019-01-01",
                'recurring_next_date': "2019-02-01",
                'date_end': "2019-01-28",
                'recurring_rule_type': "monthly",
                'recurring_invoicing_type': 'post-paid',
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_7(self):
        self.acct_line.write(
            {
                'date_end': "2019-6-05",
                'recurring_rule_type': "monthlylastday",
                'recurring_invoicing_type': 'pre-paid',
                'is_auto_renew': True,
            }
        )
        self.acct_line._onchange_date_start()
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 13)

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_forecast_period_on_contract_line_update_8(self):
        self.acct_line.write(
            {
                'date_start': "2019-01-14",
                'recurring_next_date': "2019-01-31",
                'date_end': "2019-01-14",
                'recurring_rule_type': "monthlylastday",
                'recurring_invoicing_type': 'post-paid',
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)
