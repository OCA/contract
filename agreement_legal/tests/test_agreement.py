# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAgreement(TransactionCase):
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
                "state": "active",
            }
        )

    # TEST 01: Set 'Field' for dynamic placeholder, test onchange method
    def test_onchange_copyvalue(self):
        agreement_01 = self.test_agreement
        field_01 = self.env["ir.model.fields"].search(
            [
                ("model", "=", "agreement"),
                ("name", "=", "active"),
            ]
        )
        agreement_01.field_id = field_01.id
        agreement_01.onchange_copyvalue()
        self.assertEqual(agreement_01.copyvalue, "${object.active or ''}")

    # TEST 02: Set related 'Field' for dynamic placeholder to
    # test onchange method
    def test_onchange_copyvalue2(self):
        agreement_01 = self.test_agreement
        field_01 = self.env["ir.model.fields"].search(
            [
                ("model", "=", "agreement"),
                ("name", "=", "agreement_type_id"),
            ]
        )
        sub_field_01 = self.env["ir.model.fields"].search(
            [
                ("model", "=", "agreement.type"),
                ("name", "=", "active"),
            ]
        )
        agreement_01.field_id = field_01.id
        agreement_01.onchange_copyvalue()
        self.assertEqual(agreement_01.sub_object_id.model, "agreement.type")
        agreement_01.sub_model_object_field_id = sub_field_01.id
        agreement_01.onchange_copyvalue()
        self.assertEqual(
            agreement_01.copyvalue, "${object.agreement_type_id.active or ''}"
        )

    # TEST 03: Create New Version
    def test_create_new_version(self):
        agreement_01 = self.test_agreement
        agreement_01.create_new_version()
        old_agreement = self.env["agreement"].search(
            [
                ("code", "=", agreement_01.code + "-V1"),
                ("active", "=", False),
            ]
        )
        self.assertEqual(len(old_agreement), 1)
        new_agreement = self.env["agreement"].search(
            [
                ("name", "=", "TestAgreement"),
                ("version", "=", 2),
            ]
        )
        self.assertEqual(len(new_agreement), 1)

    # TEST 04: Create New Agreement
    def test_create_new_agreement(self):
        agreement_01 = self.test_agreement
        agreement_01.create_new_agreement()
        new_agreement = self.env["agreement"].search([("name", "=", "NEW")])
        self.assertEqual(len(new_agreement), 1)

    # TEST 05: Test Description Dynamic Field
    def test_compute_dynamic_description(self):
        agreement_01 = self.test_agreement
        agreement_01.description = "${object.name}"
        self.assertEqual(agreement_01.dynamic_description,
                         "{" + str(agreement_01.id) + ": 'TestAgreement'}")

    # TEST 06: Test Parties Dynamic Field
    def test_compute_dynamic_parties(self):
        agreement_01 = self.test_agreement
        agreement_01.parties = "${object.name}"
        self.assertEqual(
            agreement_01.dynamic_parties,
            "<p>{" + str(agreement_01.id) + ": '</p><p>TestAgreement</p>'}"
        )

    # TEST 07: Test Special Terms Dynamic Field
    def test_compute_dynamic_special_terms(self):
        agreement_01 = self.test_agreement
        agreement_01.special_terms = "${object.name}"
        self.assertEqual(agreement_01.dynamic_special_terms,
                         "{" + str(agreement_01.id) + ": 'TestAgreement'}")
