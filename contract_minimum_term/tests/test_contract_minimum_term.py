# Copyright 2026 Callino - Wolfgang Pichler
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests import Form, new_test_user, tagged

from odoo.addons.base.tests.common import BaseCommon

to_date = fields.Date.to_date

# Renewal of the minimum term and termination notice: the fields of
# contract_line_successor, set on the lines.
RENEWAL_VALS = {
    "is_auto_renew": True,
    "auto_renew_interval": 12,
    "auto_renew_rule_type": "monthly",
    "termination_notice_interval": 3,
    "termination_notice_rule_type": "monthly",
}


@tagged("post_install", "-at_install")
@freeze_time("2026-09-18")
class TestContractMinimumTerm(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Internet", "list_price": 30}
        )
        cls.terminate_reason = cls.env["contract.terminate.reason"].create(
            {"name": "Customer request", "terminate_comment_required": False}
        )
        cls.min_term_vals = {
            "min_term_interval": 24,
            "min_term_rule_type": "monthly",
        }
        cls.contract = cls._create_contract(
            line_recurrence=False,
            date_start="2026-01-01",
            lines=[cls._line_vals(**RENEWAL_VALS)],
            **cls.min_term_vals,
        )
        cls.user_terminate = new_test_user(
            cls.env,
            login="terminate",
            groups="account.group_account_manager,"
            "contract_termination.can_terminate_contract",
        )
        cls.user_early_terminate = new_test_user(
            cls.env,
            login="early_terminate",
            groups="account.group_account_manager,"
            "contract_minimum_term.group_early_termination",
        )

    @classmethod
    def _line_vals(cls, **kwargs):
        vals = {
            "product_id": cls.product.id,
            "name": "Internet",
            "quantity": 1,
            "price_unit": 30,
            "recurring_rule_type": "monthly",
            "recurring_interval": 1,
        }
        vals.update(kwargs)
        return vals

    @classmethod
    def _create_contract(cls, lines=None, **kwargs):
        vals = {
            "name": "Contract",
            "partner_id": cls.partner.id,
            "recurring_rule_type": "monthly",
            "recurring_interval": 1,
        }
        vals.update(kwargs)
        # Like the contract form view does for lines without line recurrence
        line_defaults = {}
        if "date_start" in vals:
            line_defaults["date_start"] = vals["date_start"]
        vals["contract_line_ids"] = [
            Command.create({**line_defaults, **line_vals})
            for line_vals in lines or [cls._line_vals()]
        ]
        return cls.env["contract.contract"].create(vals)

    def _terminate(self, contract, terminate_date, request_date=None, user=None):
        wizard = (
            self.env["contract.contract.terminate"]
            .with_user(user or self.user_terminate)
            .create(
                {
                    "contract_id": contract.id,
                    "terminate_reason_id": self.terminate_reason.id,
                    "terminate_request_date": request_date or fields.Date.today(),
                }
            )
        )
        wizard.terminate_date = terminate_date
        return wizard.terminate_contract()

    def test_contract_level_dates(self):
        line = self.contract.contract_line_ids
        self.assertEqual(line.min_term_interval, 24)
        # An open-ended line renewing its minimum term
        self.assertTrue(line.is_auto_renew)
        self.assertFalse(line.date_end)
        self.assertEqual(line.min_term_date_end, to_date("2027-12-31"))
        self.assertEqual(line.min_term_notice_date, to_date("2027-09-30"))
        self.assertEqual(self.contract.min_term_date_end, to_date("2027-12-31"))
        self.assertEqual(self.contract.min_term_notice_date, to_date("2027-09-30"))

    def test_contract_level_change_propagates(self):
        self.contract.min_term_interval = 12
        line = self.contract.contract_line_ids
        self.assertEqual(line.min_term_interval, 12)
        self.assertEqual(line.min_term_date_end, to_date("2026-12-31"))
        self.contract.date_start = "2026-02-01"
        self.assertEqual(line.min_term_date_end, to_date("2027-01-31"))

    def test_no_minimum_term(self):
        contract = self._create_contract(
            line_recurrence=False,
            date_start="2026-01-01",
            lines=[
                self._line_vals(
                    termination_notice_interval=3,
                    termination_notice_rule_type="monthly",
                )
            ],
        )
        self.assertFalse(contract.min_term_date_end)
        # A termination notice alone does not restrict the termination
        self.assertFalse(
            contract._get_min_term_contract_termination_date(fields.Date.today())
        )
        self._terminate(contract, "2026-09-18")
        self.assertTrue(contract.is_terminated)
        self.assertFalse(contract.is_terminated_before_min_term)

    def test_renewal_on_compute(self):
        # Started long ago: already renewed several times
        contract = self._create_contract(
            line_recurrence=False,
            date_start="2020-01-01",
            lines=[self._line_vals(**RENEWAL_VALS)],
            **self.min_term_vals,
        )
        self.assertEqual(contract.min_term_date_end, to_date("2026-12-31"))
        self.assertEqual(contract.min_term_notice_date, to_date("2026-09-30"))

    def test_renewal_cron(self):
        line = self.contract.contract_line_ids
        with freeze_time("2027-09-30"):
            self.env["contract.line"]._cron_renew_minimum_term()
            self.assertEqual(line.min_term_date_end, to_date("2027-12-31"))
        with freeze_time("2027-10-01"):
            self.env["contract.line"]._cron_renew_minimum_term()
            self.assertEqual(line.min_term_date_end, to_date("2028-12-31"))
            self.assertEqual(line.min_term_notice_date, to_date("2028-09-30"))
            self.assertEqual(self.contract.min_term_date_end, to_date("2028-12-31"))
            self.assertIn(
                "renewed", self.contract.message_ids[0].body.striptags().lower()
            )

    def test_renewal_month_end(self):
        contract = self._create_contract(
            line_recurrence=False,
            date_start="2024-03-01",
            lines=[
                self._line_vals(
                    is_auto_renew=True,
                    auto_renew_interval=12,
                    auto_renew_rule_type="monthly",
                    termination_notice_interval=0,
                )
            ],
            min_term_interval=24,
        )
        line = contract.contract_line_ids
        self.assertEqual(
            line._get_min_term_date_end(line.date_start, to_date("2026-01-01")),
            to_date("2026-02-28"),
        )
        self.assertEqual(
            line._get_min_term_date_end(line.date_start, to_date("2027-03-01")),
            to_date("2028-02-29"),
        )

    def test_without_renewal(self):
        contract = self._create_contract(
            line_recurrence=False,
            date_start="2024-01-01",
            lines=[
                self._line_vals(
                    is_auto_renew=False,
                    termination_notice_interval=1,
                    termination_notice_rule_type="monthly",
                )
            ],
            min_term_interval=24,
        )
        self.assertEqual(contract.min_term_date_end, to_date("2025-12-31"))
        # Minimum term is over: only the termination notice applies
        self.assertEqual(
            contract._get_min_term_contract_termination_date(to_date("2026-09-18")),
            to_date("2026-10-18"),
        )
        with self.assertRaises(UserError):
            self._terminate(contract, "2026-10-17")
        self._terminate(contract, "2026-10-18")
        self.assertTrue(contract.is_terminated)

    def test_line_level(self):
        contract = self._create_contract(
            line_recurrence=True,
            lines=[
                self._line_vals(
                    date_start="2026-01-01", **self.min_term_vals, **RENEWAL_VALS
                ),
                self._line_vals(date_start="2026-06-01", min_term_interval=12),
                self._line_vals(date_start="2026-01-01"),
            ],
            # Contract level values are ignored with line recurrence
            min_term_interval=48,
        )
        line_1, line_2, line_3 = contract.contract_line_ids
        self.assertEqual(line_1.min_term_date_end, to_date("2027-12-31"))
        self.assertEqual(line_2.min_term_date_end, to_date("2027-05-31"))
        self.assertFalse(line_3.min_term_date_end)
        self.assertEqual(contract.min_term_date_end, to_date("2027-12-31"))
        self.assertEqual(
            contract._get_min_term_contract_termination_date(fields.Date.today()),
            to_date("2027-12-31"),
        )
        # Only the lines with a minimum term are taken into account
        self.assertEqual(contract._get_min_term_lines(), line_1 + line_2)
        # A canceled line does not restrict the termination anymore
        line_1.with_user(self.user_early_terminate).cancel()
        self.assertEqual(contract.min_term_date_end, to_date("2027-05-31"))

    def test_line_ending_before_minimum_term(self):
        contract = self._create_contract(
            line_recurrence=False,
            date_start="2026-01-01",
            lines=[self._line_vals(date_end="2026-12-31")],
            **self.min_term_vals,
        )
        line = contract.contract_line_ids
        self.assertEqual(
            line._get_min_term_earliest_termination_date(
                line.date_start, fields.Date.today()
            ),
            to_date("2026-12-31"),
        )

    def test_minimum_term_excludes_renewed_end_date(self):
        line = self.contract.contract_line_ids
        with self.assertRaises(ValidationError):
            line.date_end = "2027-12-31"

    def test_template(self):
        template = self.env["contract.template"].create(
            {
                "name": "Template",
                **self.min_term_vals,
                "contract_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": "Internet",
                            "quantity": 1,
                            "price_unit": 30,
                        }
                    )
                ],
            }
        )
        self.assertEqual(template.contract_line_ids.min_term_interval, 24)
        template.contract_line_ids.min_term_interval = 36
        contract_form = Form(self.env["contract.contract"])
        contract_form.name = "Contract from template"
        contract_form.partner_id = self.partner
        contract_form.contract_template_id = template
        contract = contract_form.save()
        self.assertEqual(contract.min_term_interval, 24)
        # Line recurrence (default with contract_line_successor): the line
        # keeps the values of the template line
        self.assertTrue(contract.line_recurrence)
        self.assertEqual(contract.contract_line_ids.min_term_interval, 36)
        self.assertTrue(contract.min_term_date_end)

    def test_wizard_defaults(self):
        wizard = self.env["contract.contract.terminate"].create(
            {
                "contract_id": self.contract.id,
                "terminate_reason_id": self.terminate_reason.id,
            }
        )
        self.assertEqual(wizard.terminate_request_date, to_date("2026-09-18"))
        self.assertEqual(wizard.min_term_earliest_date, to_date("2027-12-31"))
        self.assertEqual(wizard.terminate_date, to_date("2027-12-31"))
        self.assertFalse(wizard.is_terminated_before_min_term)
        wizard.terminate_date = "2027-06-30"
        self.assertTrue(wizard.is_terminated_before_min_term)
        # Termination received after the notice deadline: renewed term
        wizard.terminate_request_date = "2027-10-01"
        self.assertEqual(wizard.min_term_earliest_date, to_date("2028-12-31"))
        self.assertEqual(wizard.terminate_date, to_date("2028-12-31"))

    def test_terminate_before_minimum_term_refused(self):
        with self.assertRaisesRegex(UserError, "cannot be terminated before"):
            self._terminate(self.contract, "2027-06-30")
        self.assertFalse(self.contract.is_terminated)

    def test_terminate_at_minimum_term(self):
        self._terminate(self.contract, "2027-12-31")
        self.assertTrue(self.contract.is_terminated)
        self.assertFalse(self.contract.is_terminated_before_min_term)
        self.assertEqual(self.contract.terminate_request_date, to_date("2026-09-18"))
        line = self.contract.contract_line_ids
        self.assertEqual(line.date_end, to_date("2027-12-31"))
        # Stopping the line switches the renewal off, so the minimum term is
        # not renewed any more
        self.assertFalse(line.is_auto_renew)
        self.contract.with_user(
            self.user_terminate
        ).action_cancel_contract_termination()
        self.assertFalse(self.contract.terminate_request_date)

    def test_terminate_after_notice_deadline_refused(self):
        with freeze_time("2027-10-15"):
            with self.assertRaises(UserError):
                self._terminate(self.contract, "2027-12-31", request_date="2027-10-15")
            self._terminate(self.contract, "2028-12-31", request_date="2027-10-15")
        self.assertTrue(self.contract.is_terminated)

    def test_early_termination_with_group(self):
        self._terminate(self.contract, "2026-12-31", user=self.user_early_terminate)
        self.assertTrue(self.contract.is_terminated)
        self.assertTrue(self.contract.is_terminated_before_min_term)
        self.assertEqual(
            self.contract.contract_line_ids.date_end, to_date("2026-12-31")
        )
        self.assertTrue(
            any(
                "before the end of the minimum term" in message.body
                for message in self.contract.message_ids
            )
        )

    def test_line_stop_before_minimum_term_refused(self):
        line = self.contract.contract_line_ids.with_user(self.user_terminate)
        with self.assertRaisesRegex(UserError, "cannot be stopped before"):
            line.stop(to_date("2027-06-30"))
        self.assertFalse(line.date_end)
        line.stop(to_date("2027-12-31"))
        self.assertEqual(line.date_end, to_date("2027-12-31"))

    def test_line_stop_early_with_group(self):
        line = self.contract.contract_line_ids.with_user(self.user_early_terminate)
        line.stop(to_date("2026-12-31"))
        self.assertEqual(line.date_end, to_date("2026-12-31"))
        self.assertTrue(
            any(
                "before the end of the minimum term" in message.body
                for message in self.contract.message_ids
            )
        )

    def test_line_stop_wizard_defaults(self):
        line = self.contract.contract_line_ids
        action = line.action_stop()
        wizard = Form(
            self.env["contract.line.wizard"]
            .with_context(**action["context"])
            .with_user(self.user_terminate),
            view=action["views"][0][0],
        )
        self.assertEqual(wizard.min_term_request_date, to_date("2026-09-18"))
        self.assertEqual(wizard.min_term_earliest_date, to_date("2027-12-31"))
        self.assertEqual(wizard.date_end, to_date("2027-12-31"))
        self.assertFalse(wizard.is_stopped_before_min_term)
        wizard.date_end = to_date("2027-06-30")
        self.assertTrue(wizard.is_stopped_before_min_term)
        # Termination received after the notice deadline: renewed term
        wizard.min_term_request_date = to_date("2027-10-01")
        self.assertEqual(wizard.min_term_earliest_date, to_date("2028-12-31"))
        self.assertEqual(wizard.date_end, to_date("2028-12-31"))

    def test_line_stop_wizard_refuses_before_minimum_term(self):
        line = self.contract.contract_line_ids
        wizard = (
            self.env["contract.line.wizard"]
            .with_user(self.user_terminate)
            .create({"contract_line_id": line.id, "date_end": "2027-06-30"})
        )
        with self.assertRaisesRegex(UserError, "cannot be stopped before"):
            wizard.stop()
        self.assertFalse(line.date_end)

    def test_line_stop_wizard_uses_request_date(self):
        line = self.contract.contract_line_ids
        with freeze_time("2027-10-15"):
            wizard = (
                self.env["contract.line.wizard"]
                .with_user(self.user_terminate)
                .create(
                    {
                        "contract_line_id": line.id,
                        "min_term_request_date": "2027-09-15",
                        "date_end": "2027-12-31",
                    }
                )
            )
            # Received in time, entered late: the notice is still respected
            wizard.stop()
        self.assertEqual(line.date_end, to_date("2027-12-31"))

    def test_line_stop_wizard_without_minimum_term(self):
        contract = self._create_contract(date_start="2026-01-01")
        line = contract.contract_line_ids
        action = line.action_stop()
        self.assertFalse(action["context"].get("default_date_end"))
        wizard = self.env["contract.line.wizard"].create(
            {"contract_line_id": line.id, "date_end": "2026-10-31"}
        )
        self.assertFalse(wizard.min_term_earliest_date)
        self.assertFalse(wizard.is_stopped_before_min_term)

    def _stopped_line(self):
        line = self.contract.contract_line_ids
        line.with_user(self.user_terminate).stop(to_date("2027-12-31"))
        self.assertTrue(line.is_plan_successor_allowed)
        return line

    def test_plan_successor_wizard_defaults(self):
        line = self._stopped_line()
        action = line.action_plan_successor()
        wizard = Form(
            self.env["contract.line.wizard"].with_context(**action["context"]),
            view=action["views"][0][0],
        )
        wizard.date_start = to_date("2028-01-01")
        # The successor runs a minimum term of its own from its start on
        self.assertEqual(wizard.min_term_earliest_date, to_date("2029-12-31"))
        self.assertEqual(wizard.date_end, to_date("2029-12-31"))
        self.assertFalse(wizard.is_stopped_before_min_term)
        wizard.date_end = to_date("2028-06-30")
        self.assertTrue(wizard.is_stopped_before_min_term)

    def _plan_successor(self, line, date_end):
        # Not with_user(): plan_successor() reads every field of the line,
        # including those of modules the test users have no access to.
        return (
            self.env["contract.line.wizard"]
            .create(
                {
                    "contract_line_id": line.id,
                    "date_start": "2028-01-01",
                    "date_end": date_end,
                }
            )
            .plan_successor()
        )

    def test_plan_successor_before_minimum_term_refused(self):
        line = self._stopped_line()
        with self.assertRaisesRegex(UserError, "cannot end before"):
            self._plan_successor(line, "2028-06-30")
        self.assertFalse(line.successor_contract_line_id)
        self._plan_successor(line, "2029-12-31")
        self.assertEqual(
            line.successor_contract_line_id.date_end, to_date("2029-12-31")
        )

    def test_plan_successor_early_with_group(self):
        line = self._stopped_line()
        self.env.user.groups_id += self.env.ref(
            "contract_minimum_term.group_early_termination"
        )
        self._plan_successor(line, "2028-06-30")
        self.assertEqual(
            line.successor_contract_line_id.date_end, to_date("2028-06-30")
        )
        self.assertTrue(
            any(
                "before the end of the minimum term" in message.body
                for message in self.contract.message_ids
            )
        )

    def test_line_stop_skipped_by_context(self):
        # Hook for modules replacing a line by a successor (upsell/downsell)
        line = self.contract.contract_line_ids.with_user(self.user_terminate)
        line.with_context(min_term_skip_checks=True).stop(to_date("2026-12-31"))
        self.assertEqual(line.date_end, to_date("2026-12-31"))

    def test_line_cancel_only_before_start(self):
        started = self.contract.contract_line_ids.with_user(self.user_terminate)
        self.assertFalse(started.is_cancel_allowed)
        with self.assertRaisesRegex(UserError, "stopped, but not cancelled"):
            started.cancel()
        # Not started yet: still cancellable
        upcoming = self._create_contract(
            line_recurrence=False,
            date_start="2027-01-01",
            lines=[self._line_vals(**RENEWAL_VALS)],
            **self.min_term_vals,
        ).contract_line_ids.with_user(self.user_terminate)
        self.assertTrue(upcoming.is_cancel_allowed)
        upcoming.cancel()
        self.assertTrue(upcoming.is_canceled)

    def test_line_cancel_started_correction(self):
        line = self.contract.contract_line_ids
        # A user allowed to terminate early corrects a line never invoiced
        line.with_user(self.user_early_terminate).cancel()
        self.assertTrue(line.is_canceled)

    def test_line_cancel_started_and_invoiced_refused(self):
        line = self.contract.contract_line_ids
        line.write(
            {
                "recurring_next_date": "2026-07-01",
                "last_date_invoiced": "2026-06-30",
            }
        )
        with self.assertRaisesRegex(UserError, "stopped, but not cancelled"):
            line.with_user(self.user_early_terminate).cancel()
