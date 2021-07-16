# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAgreementClauses(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_customer = self.env["res.partner"].create({"name": "TestCustomer"})
        self.agreement_type = self.env["agreement.type"].create(
            {
                "name": "Test Agreement Type",
                "domain": "sale",
            }
        )
        self.test_agreement = self.env["agreement"].create(
            {
                "name": "TestAgreement",
                "description": "Test",
                "special_terms": "Test",
                "partner_id": self.test_customer.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today() + timedelta(days=365),
            }
        )
        self.test_clause = self.env["agreement.clause"].create(
            {
                "name": "TestClause",
                "title": "Test",
                "content": "Test",
                "agreement_id": self.test_agreement.id,
            }
        )

    # TEST 01: Set 'Field' for dynamic placeholder, test onchange method
    def test_onchange_copyvalue(self):
        clause_01 = self.test_clause
        field_01 = self.env["ir.model.fields"].search(
            [
                ("model", "=", "agreement.clause"),
                ("name", "=", "active"),
            ]
        )
        clause_01.field_id = field_01.id
        clause_01.onchange_copyvalue()
        self.assertEqual(clause_01.copyvalue, "${object.active or ''}")

    # TEST 02: Set related 'Field' for dynamic placeholder to
    # test onchange method
    def test_onchange_copyvalue2(self):
        clause_01 = self.test_clause
        field_01 = self.env["ir.model.fields"].search(
            [
                ("model", "=", "agreement.clause"),
                ("name", "=", "agreement_id"),
            ]
        )
        sub_field_01 = self.env["ir.model.fields"].search(
            [
                ("model", "=", "agreement"),
                ("name", "=", "active"),
            ]
        )
        clause_01.field_id = field_01.id
        clause_01.onchange_copyvalue()
        self.assertEqual(clause_01.sub_object_id.model, "agreement")
        clause_01.sub_model_object_field_id = sub_field_01.id
        clause_01.onchange_copyvalue()
        self.assertEqual(clause_01.copyvalue, "${object.agreement_id.active or ''}")

    # TEST 03: Test Dynamic Field
    def test_compute_dynamic_content(self):
        clause_01 = self.test_clause
        clause_01.content = "${object.name}"
        self.assertEqual(
            clause_01.dynamic_content,
            "<p>TestClause</p>",
        )
