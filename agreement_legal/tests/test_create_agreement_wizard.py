# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import TransactionCase


class TestCreateAgreementWizard(TransactionCase):
    def setUp(self):
        super().setUp()
        self.agreement_type = self.env["agreement.type"].create(
            {
                "name": "Test Agreement Type",
                "domain": "sale",
            }
        )
        # Create Agreement Template
        self.agreement_template = self.env["agreement"].create(
            {
                "name": "Test Agreement Template",
                "description": "Test",
                "state": "active",
                "agreement_type_id": self.agreement_type.id,
                "is_template": True,
            }
        )
        # Create Recital
        self.env["agreement.recital"].create(
            {
                "name": "Test Recital",
                "title": "Test",
                "content": "Test",
                "agreement_id": self.agreement_template.id,
            }
        )
        # Create Section
        self.section = self.env["agreement.section"].create(
            {
                "name": "Test Section",
                "title": "Test",
                "content": "Test",
                "agreement_id": self.agreement_template.id,
            }
        )
        # Create Clause
        self.env["agreement.clause"].create(
            {
                "name": "Test Clause",
                "title": "Test",
                "content": "Test",
                "agreement_id": self.agreement_template.id,
                "section_id": self.section.id,
            }
        )
        # Create Appendix
        self.env["agreement.appendix"].create(
            {
                "name": "Test Appendices",
                "title": "Test",
                "content": "Test",
                "agreement_id": self.agreement_template.id,
            }
        )

    # Test create agreement from template
    def test_create_agreement(self):
        template = self.agreement_template
        wizard = self.env["create.agreement.wizard"].create(
            {
                "template_id": self.agreement_template.id,
                "name": "Test Agreement",
            }
        )
        res = wizard.create_agreement()
        agreement = self.env[res["res_model"]].browse(res["res_id"])
        self.assertEqual(agreement.template_id, template)
        self.assertEqual(agreement.is_template, False)
        self.assertEqual(agreement.recital_ids.name, template.recital_ids.name)
        self.assertEqual(agreement.sections_ids.name, template.sections_ids.name)
        self.assertEqual(agreement.clauses_ids.name, template.clauses_ids.name)
        self.assertEqual(agreement.clauses_ids.section_id, agreement.sections_ids)
        self.assertEqual(agreement.appendix_ids.name, template.appendix_ids.name)
