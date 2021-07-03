# Copyright 2022 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestAgreementException(TransactionCase):
    def setUp(self):
        super(TestAgreementException, self).setUp()
        # Useful models
        self.Agreement = self.env["agreement"]
        self.AgreementLine = self.env["agreement.line"]
        self.partner_id = self.env.ref("base.res_partner_1")
        self.product_id_1 = self.env.ref("product.product_product_6")
        self.product_id_2 = self.env.ref("product.product_product_7")
        self.product_id_3 = self.env.ref("product.product_product_7")
        self.agreement_exception_confirm = self.env["agreement.exception.confirm"]
        self.exception_noemail = self.env.ref(
            "agreement_legal_exception.agreement_excep_no_email"
        )
        self.exception_qtycheck = self.env.ref(
            "agreement_legal_exception.agreement_excep_qty_check"
        )
        self.stage_reviewed = self.env.ref("agreement_legal.agreement_stage_reviewed")
        self.stage_new = self.env.ref("agreement_legal.agreement_stage_new")
        self.agreement_vals = {
            "name": "My Agreement",
            "partner_id": self.partner_id.id,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": self.product_id_1.name,
                        "product_id": self.product_id_1.id,
                        "qty": 5.0,
                        "uom_id": self.product_id_1.uom_po_id.id,
                    },
                ),
                (
                    0,
                    0,
                    {
                        "name": self.product_id_2.name,
                        "product_id": self.product_id_2.id,
                        "qty": 5.0,
                        "uom_id": self.product_id_1.uom_po_id.id,
                    },
                ),
            ],
        }

    def test_agreement_exception(self):
        self.exception_noemail.active = True
        self.exception_qtycheck.active = True
        self.partner_id.email = False
        self.ag = self.Agreement.create(self.agreement_vals.copy())

        # Set to reviewed
        self.ag.stage_id = self.stage_reviewed
        self.assertEqual(self.ag.stage_id, self.stage_new)
        # test all draft ag
        self.ag2 = self.Agreement.create(self.agreement_vals.copy())

        self.Agreement.detect_draft_exceptions()
        self.assertEqual(self.ag2.stage_id, self.stage_new)
        # Set ignore_exception flag  (Done after ignore is selected at wizard)
        self.ag2.ignore_exception = True
        self.ag2.stage_id = self.stage_reviewed
        self.assertEqual(self.ag2.stage_id, self.stage_reviewed)

        # Set ignore exception True  (Done manually by user)
        self.ag.ignore_exception = True
        self.ag.stage_id = self.stage_new
        self.assertTrue(not self.ag.ignore_exception)
        self.ag.stage_id = self.stage_reviewed

        # Simulation the opening of the wizard agreement_exception_confirm and
        # set ignore_exception to True
        ag_except_confirm = self.agreement_exception_confirm.with_context(
            {
                "active_id": self.ag.id,
                "active_ids": [self.ag.id],
                "active_model": self.ag._name,
            }
        ).create({"ignore": True})
        ag_except_confirm.action_confirm()
        self.assertTrue(self.ag.ignore_exception)
        self.ag.onchange_ignore_exception()
        self.assertFalse(self.ag.ignore_exception)
