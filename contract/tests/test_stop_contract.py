# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018-2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2022 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError

from .test_contract import TestContractBase


def to_date(date):
    return fields.Date.to_date(date)


class TestStopContract(TestContractBase):
    def test_stop_contract_line(self):
        """It should put end to the contract line"""
        self.acct_line.write(
            {
                "date_start": self.today,
                "recurring_next_date": self.today,
                "date_end": self.today + relativedelta(months=7),
                "is_auto_renew": True,
            }
        )
        self.acct_line.stop(self.today + relativedelta(months=5))
        self.assertEqual(self.acct_line.date_end, self.today + relativedelta(months=5))

    def test_stop_upcoming_contract_line(self):
        """It should put end to the contract line"""
        self.acct_line.write(
            {
                "date_start": self.today + relativedelta(months=3),
                "recurring_next_date": self.today + relativedelta(months=3),
                "date_end": self.today + relativedelta(months=7),
                "is_auto_renew": True,
            }
        )
        self.acct_line.stop(self.today)
        self.assertEqual(self.acct_line.date_end, self.today + relativedelta(months=7))
        self.assertTrue(self.acct_line.is_canceled)

    def test_stop_past_contract_line(self):
        """Past contract line are ignored on stop"""
        self.acct_line.write(
            {"date_end": self.today + relativedelta(months=5), "is_auto_renew": True}
        )
        self.acct_line.stop(self.today + relativedelta(months=7))
        self.assertEqual(self.acct_line.date_end, self.today + relativedelta(months=5))

    def test_stop_contract_line_without_date_end(self):
        """Past contract line are ignored on stop"""
        self.acct_line.write({"date_end": False, "is_auto_renew": False})
        self.acct_line.stop(self.today + relativedelta(months=7))
        self.assertEqual(self.acct_line.date_end, self.today + relativedelta(months=7))

    def test_stop_wizard(self):
        self.acct_line.write(
            {
                "date_start": self.today,
                "recurring_next_date": self.today,
                "date_end": self.today + relativedelta(months=5),
                "is_auto_renew": True,
            }
        )
        wizard = self.env["contract.line.wizard"].create(
            {
                "date_end": self.today + relativedelta(months=3),
                "contract_line_id": self.acct_line.id,
            }
        )
        wizard.stop()
        self.assertEqual(self.acct_line.date_end, self.today + relativedelta(months=3))
        self.assertFalse(self.acct_line.is_auto_renew)

    def test_stop_plan_successor_contract_line_0(self):
        successor_contract_line = self.acct_line.copy(
            {
                "date_start": self.today + relativedelta(months=5),
                "recurring_next_date": self.today + relativedelta(months=5),
            }
        )
        self.acct_line.write(
            {
                "successor_contract_line_id": successor_contract_line.id,
                "is_auto_renew": False,
                "date_end": self.today,
            }
        )
        suspension_start = self.today + relativedelta(months=5)
        suspension_end = self.today + relativedelta(months=6)
        with self.assertRaises(ValidationError):
            self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)

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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(self.acct_line.date_end, end_date)
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        self.assertTrue(new_line)
        new_date_end = (
            suspension_end + (end_date - suspension_start) + relativedelta(days=1)
        )
        self.assertEqual(new_line.date_start, suspension_end + relativedelta(days=1))
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        self.assertTrue(new_line)
        new_date_end = (
            end_date + (suspension_end - suspension_start) + relativedelta(days=1)
        )
        self.assertEqual(new_line.date_start, suspension_end + relativedelta(days=1))
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
                "is_auto_renew": False,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, False)
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        self.assertTrue(new_line)
        self.assertEqual(new_line.date_start, suspension_end + relativedelta(days=1))
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - start_date) + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - start_date) + timedelta(days=1),
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - start_date) + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - start_date) + timedelta(days=1),
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
                "is_auto_renew": False,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - start_date) + timedelta(days=1),
        )
        self.assertFalse(self.acct_line.date_end)
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - suspension_start) + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - suspension_start) + timedelta(days=1),
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
                "is_auto_renew": False,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - suspension_start) + timedelta(days=1),
        )
        self.assertFalse(self.acct_line.date_end)
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_stop_plan_successor_wizard(self):
        suspension_start = self.today + relativedelta(months=2)
        suspension_end = self.today + relativedelta(months=3)
        start_date = self.today + relativedelta(months=4)
        end_date = self.today + relativedelta(months=6)
        self.acct_line.write(
            {
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        wizard = self.env["contract.line.wizard"].create(
            {
                "date_start": suspension_start,
                "date_end": suspension_end,
                "is_auto_renew": False,
                "contract_line_id": self.acct_line.id,
            }
        )
        wizard.stop_plan_successor()
        self.assertEqual(
            self.acct_line.date_start,
            start_date + (suspension_end - suspension_start) + timedelta(days=1),
        )
        self.assertEqual(
            self.acct_line.date_end,
            end_date + (suspension_end - suspension_start) + timedelta(days=1),
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        self.assertFalse(new_line)

    def test_plan_successor_contract_line(self):
        self.acct_line.write(
            {
                "date_start": self.today,
                "recurring_next_date": self.today,
                "date_end": self.today + relativedelta(months=3),
                "is_auto_renew": False,
            }
        )
        self.acct_line.plan_successor(
            self.today + relativedelta(months=5),
            self.today + relativedelta(months=7),
            True,
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        self.assertFalse(self.acct_line.is_auto_renew)
        self.assertTrue(new_line.is_auto_renew)
        self.assertTrue(new_line, "should create a new contract line")
        self.assertEqual(new_line.date_start, self.today + relativedelta(months=5))
        self.assertEqual(new_line.date_end, self.today + relativedelta(months=7))

    def test_overlap(self):
        self.acct_line.write(
            {
                "date_start": self.today,
                "recurring_next_date": self.today,
                "date_end": self.today + relativedelta(months=3),
                "is_auto_renew": False,
            }
        )
        self.acct_line.plan_successor(
            self.today + relativedelta(months=5),
            self.today + relativedelta(months=7),
            True,
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        with self.assertRaises(ValidationError):
            new_line.date_start = self.today + relativedelta(months=2)
        with self.assertRaises(ValidationError):
            self.acct_line.date_end = self.today + relativedelta(months=6)

    def test_plan_successor_wizard(self):
        self.acct_line.write(
            {
                "date_start": self.today,
                "recurring_next_date": self.today,
                "date_end": self.today + relativedelta(months=2),
                "is_auto_renew": False,
            }
        )
        wizard = self.env["contract.line.wizard"].create(
            {
                "date_start": self.today + relativedelta(months=3),
                "date_end": self.today + relativedelta(months=5),
                "is_auto_renew": True,
                "contract_line_id": self.acct_line.id,
            }
        )
        wizard.plan_successor()
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        self.assertFalse(self.acct_line.is_auto_renew)
        self.assertTrue(new_line.is_auto_renew)
        self.assertTrue(new_line, "should create a new contract line")
        self.assertEqual(new_line.date_start, self.today + relativedelta(months=3))
        self.assertEqual(new_line.date_end, self.today + relativedelta(months=5))

    def test_cancel_uncancel_with_predecessor(self):
        suspension_start = self.today + relativedelta(months=3)
        suspension_end = self.today + relativedelta(months=5)
        start_date = self.today
        end_date = self.today + relativedelta(months=4)
        self.acct_line.write(
            {
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        self.assertEqual(
            self.acct_line.date_end, suspension_start - relativedelta(days=1)
        )
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
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
                "date_start": start_date,
                "recurring_next_date": start_date,
                "date_end": end_date,
            }
        )
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        new_line = self.env["contract.line"].search(
            [("predecessor_contract_line_id", "=", self.acct_line.id)]
        )
        new_line.cancel()
        suspension_start = self.today + relativedelta(months=4)
        suspension_end = self.today + relativedelta(months=5)
        self.acct_line.stop_plan_successor(suspension_start, suspension_end, True)
        with self.assertRaises(ValidationError):
            new_line.uncancel(suspension_end)

    def test_check_has_successor_is_auto_renew(self):
        with self.assertRaises(ValidationError):
            self.acct_line.plan_successor(
                to_date("2016-03-01"), to_date("2018-09-01"), False
            )

    def test_action_plan_successor(self):
        action = self.acct_line.action_plan_successor()
        self.assertEqual(
            action["context"]["default_contract_line_id"], self.acct_line.id
        )

    def test_action_stop(self):
        action = self.acct_line.action_stop()
        self.assertEqual(
            action["context"]["default_contract_line_id"], self.acct_line.id
        )

    def test_action_stop_plan_successor(self):
        action = self.acct_line.action_stop_plan_successor()
        self.assertEqual(
            action["context"]["default_contract_line_id"], self.acct_line.id
        )

    def test_stop_at_last_date_invoiced(self):
        self.contract.recurring_create_invoice()
        self.assertTrue(self.acct_line.recurring_next_date)
        self.acct_line.stop(self.acct_line.last_date_invoiced)
        self.assertFalse(self.acct_line.recurring_next_date)

    def test_stop_and_update_recurring_invoice_date(self):
        self.acct_line.write(
            {
                "date_start": "2019-01-01",
                "date_end": "2019-12-31",
                "recurring_next_date": "2020-01-01",
                "recurring_invoicing_type": "post-paid",
                "recurring_rule_type": "yearly",
            }
        )
        self.acct_line.stop(to_date("2019-05-31"))
        self.assertEqual(self.acct_line.date_end, to_date("2019-05-31"))
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2019-06-01"))

    @freeze_time("2018-02-15")
    def test_contract_stop_plan_global(self):
        """
        Use a contract with several lines and global recurrence
        Stop lines and plan successor
        """
        self._create_contract_global()
        self.contract_global.recurring_create_invoice()
        invoices = self.contract_global._get_related_invoices()
        self.assertEqual(
            self.contract_global.recurring_next_date, fields.Date.to_date("2018-03-15")
        )
        self.assertEqual(fields.Date.to_date("2018-02-15"), invoices.invoice_date)
        self.contract_global.mapped("contract_line_ids").stop_plan_successor(
            fields.Date.to_date("2018-04-01"), fields.Date.to_date("2018-05-14"), False
        )

    @freeze_time("2018-02-15")
    def test_stop_all_lines_and_plan_successor(self):
        self._create_global_contract_several_lines()
        self.contract_global_multi.recurring_create_invoice()
        self.contract_global_multi.contract_line_ids.invalidate_cache()
        self.assertEqual(
            ["weekly", "weekly"],
            self.contract_global_multi.contract_line_ids.mapped("recurring_rule_type"),
        )

        self.assertEqual(
            fields.Date.to_date("2018-02-22"),
            self.contract_global_multi.recurring_next_date,
        )
        lines_before = self.contract_global_multi.contract_line_ids
        self.contract_global_multi.contract_line_ids.stop_plan_successor(
            fields.Date.to_date("2018-02-22"), fields.Date.to_date("2018-03-01"), False
        )
        self.assertTrue(
            all(not line_before.next_period_date_start for line_before in lines_before)
        )
