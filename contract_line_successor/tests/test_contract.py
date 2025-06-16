# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo.exceptions import ValidationError

from odoo.addons.contract.tests.test_contract import (
    TestContract,
    to_date,
)


class TestContractSuccessor(TestContract):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract.company_id.create_new_line_at_contract_line_renew = True
        cls.line_vals.update({"is_auto_renew": False})

    def test_date_end(self):
        """recurring next date for a contract is the min for all lines"""
        self.acct_line.date_end = "2018-01-01"
        self.acct_line.copy()
        self.acct_line.write({"date_end": False, "is_auto_renew": False})
        self.assertFalse(self.contract.date_end)

    def test_cancel_contract_line(self):
        """It should raise a validation error"""
        self.acct_line.cancel()
        with self.assertRaises(ValidationError):
            self.acct_line.stop(self.today)

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

    def test_cancel(self):
        self.acct_line.write(
            {"date_end": self.today + relativedelta(months=5), "is_auto_renew": True}
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
        wizard = self.env["contract.line.wizard"].create(
            {"recurring_next_date": self.today, "contract_line_id": self.acct_line.id}
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

    def test_check_has_not_date_end_has_successor(self):
        self.acct_line.write({"date_end": False, "is_auto_renew": False})
        with self.assertRaises(ValidationError):
            self.acct_line.plan_successor(
                to_date("2016-03-01"), to_date("2016-09-01"), False
            )

    def test_check_has_not_date_end_is_auto_renew(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write({"date_end": False, "is_auto_renew": True})

    def test_check_has_successor_is_auto_renew(self):
        with self.assertRaises(ValidationError):
            self.acct_line.plan_successor(
                to_date("2016-03-01"), to_date("2018-09-01"), False
            )

    def test_search_contract_line_to_renew(self):
        self.acct_line.write({"date_end": self.today, "is_auto_renew": True})
        line_1 = self.acct_line.copy({"date_end": self.today + relativedelta(months=1)})
        line_2 = self.acct_line.copy({"date_end": self.today - relativedelta(months=1)})
        line_3 = self.acct_line.copy({"date_end": self.today - relativedelta(months=2)})
        line_4 = self.acct_line.copy({"date_end": self.today + relativedelta(months=2)})
        to_renew = self.acct_line.search(
            self.acct_line._contract_line_to_renew_domain()
        )
        self.assertEqual(set(to_renew), {self.acct_line, line_1, line_2, line_3})
        self.acct_line.cron_renew_contract_line()
        self.assertTrue(self.acct_line.successor_contract_line_id)
        self.assertTrue(line_1.successor_contract_line_id)
        self.assertTrue(line_2.successor_contract_line_id)
        self.assertTrue(line_3.successor_contract_line_id)
        self.assertFalse(line_4.successor_contract_line_id)

    def test_renew_create_new_line(self):
        date_start = self.today - relativedelta(months=9)
        date_end = date_start + relativedelta(months=12) - relativedelta(days=1)
        self.acct_line.write(
            {
                "is_auto_renew": True,
                "date_start": date_start,
                "recurring_next_date": date_start,
                "date_end": self.today,
            }
        )
        self.acct_line._onchange_is_auto_renew()
        self.assertEqual(self.acct_line.date_end, date_end)
        new_line = self.acct_line.renew()
        self.assertFalse(self.acct_line.is_auto_renew)
        self.assertTrue(new_line.is_auto_renew)
        self.assertEqual(new_line.date_start, date_start + relativedelta(months=12))
        self.assertEqual(new_line.date_end, date_end + relativedelta(months=12))

    def test_renew_extend_original_line(self):
        self.contract.company_id.create_new_line_at_contract_line_renew = False
        date_start = self.today - relativedelta(months=9)
        date_end = date_start + relativedelta(months=12) - relativedelta(days=1)
        self.acct_line.write(
            {
                "is_auto_renew": True,
                "date_start": date_start,
                "recurring_next_date": date_start,
                "date_end": self.today,
            }
        )
        self.acct_line._onchange_is_auto_renew()
        self.assertEqual(self.acct_line.date_end, date_end)
        self.acct_line.renew()
        self.assertTrue(self.acct_line.is_auto_renew)
        self.assertEqual(self.acct_line.date_start, date_start)
        self.assertEqual(self.acct_line.date_end, date_end + relativedelta(months=12))

    def test_unlink(self):
        with self.assertRaises(ValidationError):
            self.acct_line.unlink()

    def test_contract_line_state(self):
        lines = self.env["contract.line"]
        # upcoming
        lines |= self.acct_line.copy(
            {
                "date_start": self.today + relativedelta(months=3),
                "recurring_next_date": self.today + relativedelta(months=3),
                "date_end": self.today + relativedelta(months=5),
            }
        )
        # in-progress
        lines |= self.acct_line.copy(
            {
                "date_start": self.today,
                "recurring_next_date": self.today,
                "date_end": self.today + relativedelta(months=5),
            }
        )
        # in-progress
        lines |= self.acct_line.copy(
            {
                "date_start": self.today,
                "recurring_next_date": self.today,
                "date_end": self.today + relativedelta(months=5),
                "manual_renew_needed": True,
            }
        )
        # to-renew
        lines |= self.acct_line.copy(
            {
                "date_start": self.today - relativedelta(months=5),
                "recurring_next_date": self.today - relativedelta(months=5),
                "date_end": self.today - relativedelta(months=2),
                "manual_renew_needed": True,
            }
        )
        # upcoming-close
        lines |= self.acct_line.copy(
            {
                "date_start": self.today - relativedelta(months=5),
                "recurring_next_date": self.today - relativedelta(months=5),
                "date_end": self.today + relativedelta(days=20),
                "is_auto_renew": False,
            }
        )
        # closed
        lines |= self.acct_line.copy(
            {
                "date_start": self.today - relativedelta(months=5),
                "recurring_next_date": self.today - relativedelta(months=5),
                "date_end": self.today - relativedelta(months=2),
                "is_auto_renew": False,
            }
        )
        # canceled
        lines |= self.acct_line.copy(
            {
                "date_start": self.today - relativedelta(months=5),
                "recurring_next_date": self.today - relativedelta(months=5),
                "date_end": self.today - relativedelta(months=2),
                "is_canceled": True,
            }
        )
        # section
        lines |= self.env["contract.line"].create(
            {
                "contract_id": self.contract.id,
                "display_type": "line_section",
                "name": "Test section",
            }
        )
        states = [
            "upcoming",
            "in-progress",
            "to-renew",
            "upcoming-close",
            "closed",
            "canceled",
            False,
        ]
        self.assertEqual(set(lines.mapped("state")), set(states))
        # Test search method
        lines.flush_recordset()  # Needed for computed stored fields
        # like termination_notice_date
        for state in states:
            lines = self.env["contract.line"].search([("state", "=", state)])
            self.assertTrue(lines, state)
            self.assertTrue(state in lines.mapped("state"), state)
            lines = self.env["contract.line"].search([("state", "!=", state)])
            self.assertFalse(state in lines.mapped("state"), state)
        lines = self.env["contract.line"].search([("state", "in", states)])
        self.assertEqual(set(lines.mapped("state")), set(states))
        lines = self.env["contract.line"].search([("state", "in", [])])
        self.assertFalse(lines.mapped("state"))
        with self.assertRaises(TypeError):
            self.env["contract.line"].search([("state", "in", "upcoming")])
        lines = self.env["contract.line"].search([("state", "not in", [])])
        self.assertEqual(set(lines.mapped("state")), set(states))
        lines = self.env["contract.line"].search([("state", "not in", states)])
        self.assertFalse(lines.mapped("state"))
        state2 = ["upcoming", "in-progress"]
        lines = self.env["contract.line"].search([("state", "not in", state2)])
        self.assertEqual(set(lines.mapped("state")), set(states) - set(state2))

    def test_check_auto_renew_contract_line_with_successor(self):
        """
        A contract line with a successor can't be set to auto-renew
        """
        successor_contract_line = self.acct_line.copy()
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    "is_auto_renew": True,
                    "successor_contract_line_id": successor_contract_line.id,
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
                    "date_end": False,
                    "successor_contract_line_id": successor_contract_line.id,
                }
            )

    def test_delay_invoiced_contract_line(self):
        self.acct_line.write(
            {"last_date_invoiced": self.acct_line.date_start + relativedelta(days=1)}
        )
        with self.assertRaises(ValidationError):
            self.acct_line._delay(relativedelta(months=1))

    def test_cancel_invoiced_contract_line(self):
        self.acct_line.write(
            {"last_date_invoiced": self.acct_line.date_start + relativedelta(days=1)}
        )
        with self.assertRaises(ValidationError):
            self.acct_line.cancel()

    def test_action_uncancel(self):
        action = self.acct_line.action_uncancel()
        self.assertEqual(
            action["context"]["default_contract_line_id"], self.acct_line.id
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

    def test_check_last_date_invoiced_before_next_invoice_date(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    "date_start": "2019-01-01",
                    "date_end": "2019-12-01",
                    "recurring_next_date": "2019-01-01",
                    "last_date_invoiced": "2019-06-01",
                }
            )

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

    def test_contract_template_is_auto_renew(self):
        contract_template = self.env["contract.template"].create(
            {
                "name": "Template Auto Renew Test",
                "contract_line_ids": [
                    (0, 0, {"name": "Line 1", "is_auto_renew": True}),
                    (0, 0, {"name": "Line 2", "is_auto_renew": True}),
                ],
            }
        )
        self.assertTrue(contract_template.is_auto_renew)
        contract_template.contract_line_ids[1].write({"is_auto_renew": False})
        self.assertFalse(contract_template.is_auto_renew)
