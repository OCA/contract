# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.exceptions import UserError, ValidationError

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
