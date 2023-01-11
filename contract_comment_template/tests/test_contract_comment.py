# Copyright 2023 elegosoft (https://www.elegosoft.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractInvoiceComment(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.ref("base.main_company")
        cls.base_comment_model = cls.env["base.comment.template"]
        # Create comment related to contract.contract model
        cls.contract_obj = cls.env.ref("contract.model_contract_contract")
        cls.contract_before_comment = cls._create_comment(
            cls.contract_obj, "before_lines"
        )
        cls.contract_after_comment = cls._create_comment(
            cls.contract_obj, "after_lines"
        )
        # Create comment related to move model
        cls.move_obj = cls.env.ref("account.model_account_move")
        cls.move_before_comment = cls._create_comment(cls.move_obj, "before_lines")
        cls.move_after_comment = cls._create_comment(cls.move_obj, "after_lines")
        # Create partner
        cls.comment_partner = cls.env["res.partner"].create({"name": "Partner Test"})
        cls.comment_partner.base_comment_template_ids = [
            (4, cls.contract_before_comment.id),
            (4, cls.contract_after_comment.id),
            (4, cls.move_before_comment.id),
            (4, cls.move_after_comment.id),
        ]
        cls.comment_contract = cls.contract2.copy(
            {
                "name": "Test Contract Comment",
            }
        )
        cls.comment_contract.partner_id = cls.comment_partner.id
        cls.comment_contract._onchange_partner_id()

    @classmethod
    def _create_comment(cls, model, position):
        return cls.base_comment_model.create(
            {
                "name": "Comment " + position,
                "company_id": cls.company.id,
                "position": position,
                "text": "Text " + position,
                "model_ids": [(6, 0, model.ids)],
            }
        )

    def test_comments_in_contract_report(self):
        res = (
            self.env["ir.actions.report"]
            ._get_report_from_name("contract.report_contract_document")
            ._render_qweb_html(self.comment_contract.ids)
        )
        self.assertRegex(str(res[0]), self.contract_before_comment.text)
        self.assertRegex(str(res[0]), self.contract_after_comment.text)

    def test_comments_in_generated_invoice_from_contract(self):
        invoice = self.comment_contract.recurring_create_invoice()
        self.assertTrue(self.move_before_comment in invoice.comment_template_ids)
        self.assertTrue(self.move_after_comment in invoice.comment_template_ids)
        self.assertFalse(self.contract_before_comment in invoice.comment_template_ids)
        self.assertFalse(self.contract_after_comment in invoice.comment_template_ids)
        res = (
            self.env["ir.actions.report"]
            ._get_report_from_name("account.report_invoice")
            ._render_qweb_html(invoice.ids)
        )
        self.assertRegex(str(res[0]), self.move_before_comment.text)
        self.assertRegex(str(res[0]), self.move_after_comment.text)

    def test_comments_in_contract(self):
        self.assertTrue(
            self.contract_after_comment in self.comment_contract.comment_template_ids
        )
        self.assertTrue(
            self.contract_before_comment in self.comment_contract.comment_template_ids
        )
