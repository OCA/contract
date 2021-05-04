# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestAgreementServiceProfile(TransactionCase):
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
        self.test_serviceprofile = self.env["agreement.serviceprofile"].create(
            {
                "name": "TestServiceProfile",
                "agreement_id": self.test_agreement.id,
            }
        )

    # TEST 01: Check Default Stage
    def test_default_stage_id(self):
        sp_01 = self.test_serviceprofile
        self.assertEqual(sp_01.stage_id.name, "Draft")

    # TEST 02: Check Read Stages
    def test_read_group_stage_ids(self):
        sp_01 = self.test_serviceprofile
        self.assertEqual(
            sp_01._read_group_stage_ids(self.env["agreement.stage"], [], "id"),
            self.env["agreement.stage"].search(
                [("stage_type", "=", "serviceprofile")],
                order="id",
            ),
        )
