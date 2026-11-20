# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo.fields import Date

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractLineForecastPeriod(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, queue_job__no_delay=True))
        cls.this_year = Date.today().year
        cls.line_vals["date_start"] = Date.today()
        cls.line_vals["recurring_next_date"] = Date.today()
        cls.acct_line = cls.env["contract.line"].create(cls.line_vals)

    def test_forecast_period_creation(self):
        self.acct_line.write(
            {
                "date_start": f"{self.this_year}-01-01",
                "recurring_next_date": f"{self.this_year}-01-01",
                "date_end": f"{self.this_year}-12-31",
                "recurring_rule_type": "monthly",
                "recurring_invoicing_type": "pre-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 12)

    def test_forecast_period_on_contract_line_update_1(self):
        self.acct_line.write(
            {
                "date_start": f"{self.this_year}-01-01",
                "recurring_next_date": f"{self.this_year}-01-01",
                "date_end": f"{self.this_year}-12-31",
                "recurring_rule_type": "yearly",
                "recurring_invoicing_type": "pre-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)

    def test_forecast_period_on_contract_line_update_2(self):
        self.acct_line.write(
            {
                "date_start": f"{self.this_year}-01-01",
                "recurring_next_date": f"{self.this_year}-01-31",
                "date_end": f"{self.this_year}-06-05",
                "recurring_rule_type": "monthlylastday",
                "recurring_invoicing_type": "pre-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 6)

    def test_forecast_period_on_contract_line_update_3(self):
        self.assertEqual(self.acct_line.price_subtotal, 50)
        self.acct_line.write({"price_unit": 50})
        self.assertEqual(self.acct_line.price_subtotal, 25)
        self.assertEqual(self.acct_line.forecast_period_ids[0].price_subtotal, 25)

    def test_forecast_period_on_contract_line_update_4(self):
        self.assertEqual(self.acct_line.price_subtotal, 50)
        self.acct_line.write({"discount": 0})
        self.assertEqual(self.acct_line.price_subtotal, 100)
        self.assertEqual(self.acct_line.forecast_period_ids[0].price_subtotal, 100)

    def test_forecast_period_on_contract_line_update_5(self):
        self.acct_line.cancel()
        self.assertFalse(self.acct_line.forecast_period_ids)

    def test_forecast_period_on_contract_line_update_6(self):
        self.acct_line.write(
            {
                "date_start": f"{self.this_year}-01-01",
                "recurring_next_date": f"{self.this_year}-01-01",
                "date_end": f"{self.this_year}-01-28",
                "recurring_rule_type": "monthly",
                "recurring_invoicing_type": "pre-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)

    def test_forecast_period_on_contract_line_update_7(self):
        self.acct_line.write(
            {
                "date_start": f"{self.this_year}-01-01",
                "recurring_next_date": f"{self.this_year}-02-01",
                "date_end": f"{self.this_year}-01-28",
                "recurring_rule_type": "monthly",
                "recurring_invoicing_type": "post-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)

    def test_forecast_period_on_contract_line_update_8(self):
        self.acct_line.write(
            {
                "date_end": Date.today() + relativedelta(months=3),
                "recurring_rule_type": "monthlylastday",
                "recurring_invoicing_type": "pre-paid",
                "is_auto_renew": False,
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 4)
        self.acct_line.write({"is_auto_renew": True})
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 12)

    def test_forecast_period_on_contract_line_update_9(self):
        self.acct_line.write(
            {
                "date_start": f"{self.this_year}-01-14",
                "recurring_next_date": f"{self.this_year}-01-31",
                "date_end": f"{self.this_year}-01-14",
                "recurring_rule_type": "monthlylastday",
                "recurring_invoicing_type": "post-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 1)

    def test_forecast_period_on_contract_line_update_10(self):
        self.acct_line.write(
            {
                "date_start": "2019-01-14",
                "recurring_next_date": "2019-01-31",
                "date_end": "2020-01-14",
                "recurring_rule_type": "monthlylastday",
                "last_date_invoiced": False,
                "recurring_invoicing_type": "post-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 13)
        self.assertEqual(
            (
                self.acct_line.forecast_period_ids[0].date_start,
                self.acct_line.forecast_period_ids[0].date_end,
                self.acct_line.forecast_period_ids[0].date_invoice,
            ),
            (
                Date.to_date("2019-01-14"),
                Date.to_date("2019-01-31"),
                Date.to_date("2019-01-31"),
            ),
        )
        self.assertEqual(
            (
                self.acct_line.forecast_period_ids[1].date_start,
                self.acct_line.forecast_period_ids[1].date_end,
                self.acct_line.forecast_period_ids[1].date_invoice,
            ),
            (
                Date.to_date("2019-02-01"),
                Date.to_date("2019-02-28"),
                Date.to_date("2019-02-28"),
            ),
        )
        self.assertEqual(
            (
                self.acct_line.forecast_period_ids[-1].date_start,
                self.acct_line.forecast_period_ids[-1].date_end,
                self.acct_line.forecast_period_ids[-1].date_invoice,
            ),
            (
                Date.to_date("2020-01-01"),
                Date.to_date("2020-01-14"),
                Date.to_date("2020-01-14"),
            ),
        )

    def test_forecast_period_on_contract_line_update_11(self):
        self.acct_line.write(
            {
                "date_start": "2019-01-14",
                "recurring_next_date": "2019-01-14",
                "date_end": "2020-01-14",
                "recurring_rule_type": "monthlylastday",
                "last_date_invoiced": False,
                "recurring_invoicing_type": "pre-paid",
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 13)
        self.assertEqual(
            (
                self.acct_line.forecast_period_ids[0].date_start,
                self.acct_line.forecast_period_ids[0].date_end,
                self.acct_line.forecast_period_ids[0].date_invoice,
            ),
            (
                Date.to_date("2019-01-14"),
                Date.to_date("2019-01-31"),
                Date.to_date("2019-01-14"),
            ),
        )
        self.assertEqual(
            (
                self.acct_line.forecast_period_ids[1].date_start,
                self.acct_line.forecast_period_ids[1].date_end,
                self.acct_line.forecast_period_ids[1].date_invoice,
            ),
            (
                Date.to_date("2019-02-01"),
                Date.to_date("2019-02-28"),
                Date.to_date("2019-02-01"),
            ),
        )
        self.assertEqual(
            (
                self.acct_line.forecast_period_ids[-1].date_start,
                self.acct_line.forecast_period_ids[-1].date_end,
                self.acct_line.forecast_period_ids[-1].date_invoice,
            ),
            (
                Date.to_date("2020-01-01"),
                Date.to_date("2020-01-14"),
                Date.to_date("2020-01-01"),
            ),
        )

    def test_forecast_period_for_auto_renew_contract(self):
        """If a contract line is set to auto renew the forecast should continue
        after the date end and stop at the company forecast period"""
        # Set the company forecast period to three years
        self.acct_line.contract_id.company_id.contract_forecast_interval = 36
        self.acct_line.write(
            {
                "date_start": Date.today(),
                "recurring_next_date": Date.today(),
                "date_end": Date.today() + relativedelta(years=1),
                "recurring_rule_type": "monthlylastday",
                "last_date_invoiced": False,
                "recurring_invoicing_type": "pre-paid",
                "is_auto_renew": False,
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 13)

        self.acct_line.write({"is_auto_renew": True})
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 36)

    def test_forecast_period_for_undefined_date_end_contract(self):
        """If a contract line have and undefined date end the forecast should
        continue to the company forecast period"""
        self.acct_line.contract_id.company_id.contract_forecast_interval = 36
        self.acct_line.write(
            {
                "date_start": Date.today(),
                "recurring_next_date": Date.today(),
                "date_end": Date.today() + relativedelta(years=1),
                "recurring_rule_type": "monthlylastday",
                "last_date_invoiced": False,
                "recurring_invoicing_type": "pre-paid",
                "is_auto_renew": False,
            }
        )
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 13)

        self.acct_line.write({"date_end": False})
        self.assertTrue(self.acct_line.forecast_period_ids)
        self.assertEqual(len(self.acct_line.forecast_period_ids), 36)
