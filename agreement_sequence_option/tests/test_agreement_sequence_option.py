# Copyright 2023 Ecosoft Co., Ltd. (https://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestAgreementSequenceOption(TransactionCase):
    def setUp(self):
        super(TestAgreementSequenceOption, self).setUp()
        self.Agreement = self.env["agreement"]
        self.agreement_type = self.env["agreement.type"].create(
            {
                "name": "Test Agreement Type",
                "domain": "sale",
            }
        )
        self.ag_vals = {
            "name": "Test",
            "description": "Test",
            "state": "active",
            "agreement_type_id": self.agreement_type.id,
        }
        self.ag_seq_opt = self.env.ref(
            "agreement_sequence_option.agreement_sequence_option"
        )

    def test_agreement_sequence_options(self):
        """test with and without sequence option activated"""
        # With sequence option
        self.ag_seq_opt.use_sequence_option = True
        self.ag = self.Agreement.create(self.ag_vals.copy())
        self.assertIn("AG-1", self.ag.code)
        self.ag_copy = self.ag.copy()
        self.assertIn("AG-1", self.ag_copy.code)
        # Without sequence option
        self.ag_seq_opt.use_sequence_option = False
        self.ag = self.Agreement.create(self.ag_vals.copy())
        self.assertNotIn("AG-1", self.ag.code)
        self.ag_copy = self.ag.copy()
        self.assertNotIn("AG-1", self.ag_copy.code)
