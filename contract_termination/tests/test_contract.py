# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import Command, fields
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

from odoo.addons.contract_line_successor.tests.test_contract import (
    TestContractSuccessor,
    to_date,
)


class TestContractTermination(TestContractSuccessor):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.terminate_reason = cls.env["contract.terminate.reason"].create(
            {"name": "terminate_reason"}
        )

    def test_action_terminate_contract(self):
        action = self.contract.action_terminate_contract()
        wizard = (
            self.env[action["res_model"]]
            .with_context(**action["context"])
            .create(
                {
                    "terminate_date": "2018-03-01",
                    "terminate_reason_id": self.terminate_reason.id,
                    "terminate_comment": "terminate_comment",
                }
            )
        )
        self.assertEqual(wizard.contract_id, self.contract)
        with self.assertRaises(UserError):
            wizard.terminate_contract()
        group_can_terminate_contract = self.env.ref(
            "contract_termination.can_terminate_contract"
        )
        group_can_terminate_contract.users |= self.env.user
        wizard.terminate_contract()
        self.assertTrue(self.contract.is_terminated)
        self.assertEqual(self.contract.terminate_date, to_date("2018-03-01"))
        self.assertEqual(self.contract.terminate_reason_id.id, self.terminate_reason.id)
        self.assertEqual(self.contract.terminate_comment, "terminate_comment")
        self.contract.action_cancel_contract_termination()
        self.assertFalse(self.contract.is_terminated)
        self.assertFalse(self.contract.terminate_reason_id)
        self.assertFalse(self.contract.terminate_comment)

    def test_terminate_date_before_last_date_invoiced(self):
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-14"))
        group_can_terminate_contract = self.env.ref(
            "contract_termination.can_terminate_contract"
        )
        group_can_terminate_contract.users |= self.env.user
        with self.assertRaises(ValidationError):
            self.contract._terminate_contract(
                self.terminate_reason,
                "terminate_comment",
                to_date("2018-02-13"),
            )
        # Try terminate contract line with last_date_invoiced allowed
        self.contract._terminate_contract(
            self.terminate_reason,
            "terminate_comment",
            to_date("2018-02-13"),
            terminate_lines_with_last_date_invoiced=True,
        )
        self.assertTrue(self.contract.is_terminated)
        self.assertEqual(self.acct_line.date_end, to_date("2018-02-14"))

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

    def _search_filter_domain(self, filter_name):
        """Return the domain the contract search view actually ships."""
        arch = self.env["contract.contract"].get_view(
            self.env.ref("contract.contract_contract_search_view").id, "search"
        )["arch"]
        node = etree.fromstring(arch).xpath(f"//filter[@name='{filter_name}']")[0]
        return safe_eval(
            node.get("domain"),
            {"context_today": lambda: fields.Date.context_today(self.contract)},
        )

    def _running_contract(self, date_end):
        """A contract whose end date is in the future, hence 'in progress'."""
        return self.env["contract.contract"].create(
            {
                "name": "Contract to terminate",
                "partner_id": self.partner.id,
                "pricelist_id": self.partner.property_product_pricelist.id,
                "contract_type": "sale",
                "line_recurrence": True,
                "contract_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product_1.id,
                            "name": "Services",
                            "quantity": 1,
                            "uom_id": self.product_1.uom_id.id,
                            "price_unit": 100,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": self.today,
                            "recurring_next_date": self.today,
                            "date_end": date_end,
                        }
                    )
                ],
            }
        )

    def _terminate(self, contract, terminate_date):
        self.env.ref(
            "contract_termination.can_terminate_contract"
        ).users |= self.env.user
        action = contract.action_terminate_contract()
        self.env[action["res_model"]].with_context(**action["context"]).create(
            {
                "terminate_date": terminate_date,
                "terminate_reason_id": self.terminate_reason.id,
                "terminate_comment": "terminate_comment",
            }
        ).terminate_contract()

    def test_in_progress_filter_excludes_terminated_contract(self):
        """A terminated contract must leave the 'In progress' filter at once.

        Terminating a contract that was already invoiced ahead stops its lines
        at the last invoiced date, which leaves date_end in the future. A
        purely date based filter would therefore keep listing the contract as
        running for the whole remaining invoiced period.
        """
        contract = self._running_contract(self.today + relativedelta(years=1))
        domain = self._search_filter_domain("not_finished")
        self.assertIn(contract, self.env["contract.contract"].search(domain))

        self._terminate(contract, self.today)

        self.assertTrue(contract.is_terminated)
        # The date based part of the filter still matches, so only
        # is_terminated can keep the contract out of the list.
        self.assertGreaterEqual(contract.date_end, self.today)
        self.assertNotIn(contract, self.env["contract.contract"].search(domain))

    def test_terminated_filter_lists_terminated_contract(self):
        contract = self._running_contract(self.today + relativedelta(years=1))
        domain = self._search_filter_domain("terminated")
        self.assertNotIn(contract, self.env["contract.contract"].search(domain))

        self._terminate(contract, self.today)

        self.assertIn(contract, self.env["contract.contract"].search(domain))

    def test_cancelling_termination_restores_in_progress(self):
        contract = self._running_contract(self.today + relativedelta(years=1))
        self._terminate(contract, self.today)
        contract.action_cancel_contract_termination()

        self.assertFalse(contract.is_terminated)
        domain = self._search_filter_domain("not_finished")
        self.assertIn(contract, self.env["contract.contract"].search(domain))
