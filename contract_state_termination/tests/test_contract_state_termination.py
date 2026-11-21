# Copyright 2026 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from lxml import etree

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestContractStateTermination(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.env["res.partner"].create({"name": "Customer"})
        product = cls.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Terminated in the end",
                "partner_id": partner.id,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": product.id,
                            "name": "Service",
                            "quantity": 1,
                            "price_unit": 100,
                            "date_start": "2018-01-01",
                            "recurring_next_date": "2018-01-31",
                        },
                    )
                ],
            }
        )
        cls.terminate_reason = cls.env["contract.terminate.reason"].create(
            {"name": "Returned"}
        )
        cls.env.ref("contract_termination.can_terminate_contract").write(
            {"user_ids": [(4, cls.env.user.id)]}
        )

    def _terminate(self):
        self.contract.state = "active"
        self.contract._terminate_contract(
            self.terminate_reason, "returned", date(2018, 2, 15)
        )

    def test_terminating_sets_the_state(self):
        self._terminate()
        self.assertTrue(self.contract.is_terminated)
        self.assertEqual(self.contract.state, "terminated")

    def test_cancelling_the_termination_reactivates(self):
        self._terminate()
        self.contract.action_cancel_contract_termination()
        self.assertFalse(self.contract.is_terminated)
        self.assertEqual(self.contract.state, "active")

    def test_cancelling_leaves_other_states_alone(self):
        """Only a contract this module terminated is put back to active."""
        self.contract.state = "draft"
        self.contract.action_cancel_contract_termination()
        self.assertEqual(self.contract.state, "draft")

    def test_a_terminated_contract_may_still_invoice(self):
        self._terminate()
        self.assertIn("terminated", self.contract._get_invoiceable_states())

    def test_existing_terminations_are_synced(self):
        self.contract.write({"is_terminated": True, "state": "active"})
        self.env["contract.contract"]._sync_terminated_state()
        self.assertEqual(self.contract.state, "terminated")

    def test_setting_the_flag_directly_follows_too(self):
        """A module that terminates without the wizard gets the state too."""
        self.contract.state = "active"
        self.contract.is_terminated = True
        self.assertEqual(self.contract.state, "terminated")
        self.contract.is_terminated = False
        self.assertEqual(self.contract.state, "active")

    def test_only_an_active_contract_can_be_terminated(self):
        self.contract.state = "draft"
        with self.assertRaises(UserError):
            self.contract.action_terminate_contract()
        self.contract.state = "active"
        action = self.contract.action_terminate_contract()
        self.assertEqual(action["res_model"], "contract.contract.terminate")
        self._terminate()
        # The details of a terminated contract can still be updated.
        self.assertTrue(self.contract.action_terminate_contract())

    def test_buttons_keep_the_other_conditions(self):
        """The state conditions are added to, not replacing, the base ones."""
        arch = self.env["contract.contract"].get_view(view_type="form")["arch"]
        if isinstance(arch, bytes):
            arch = arch.decode()
        doc = etree.fromstring(arch)

        def invisible(name):
            return " ".join(
                button.get("invisible", "")
                for button in doc.iter("button")
                if button.get("name") == name
            )

        self.assertIn("state == 'active'", invisible("action_activate"))
        self.assertIn("state == 'terminated'", invisible("action_activate"))
        self.assertIn("state == 'draft'", invisible("action_draft"))
        self.assertIn("state == 'terminated'", invisible("action_draft"))
        self.assertIn("state != 'active'", invisible("action_terminate_contract"))
