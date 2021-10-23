# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo import fields


class TestAgreementMaintenance(common.TransactionCase):
    def setUp(self):
        super(TestAgreementMaintenance, self).setUp()

        self.agreement_obj = self.env["agreement"]
        self.agreement_type_id = self.env["agreement.type"].create(
            {"name": "Test Agreement Type", "active": True}
        )
        self.product = self.env.ref("product.product_product_8_product_template")

    def test_fieldservice_purchase(self):
        agreement_vals = {
            "name": "Test Agreement",
            "agreement_type_id": self.agreement_type_id.id,
            "description": "Test Agreement",
            "start_date": fields.Date.today(),
            "end_date": fields.Date.today(),
        }
        agreement = self.agreement_obj.create(agreement_vals)

        maintenance_req = self.env.ref("maintenance.m_request_7")
        maintenance_req.write({"agreement_id": agreement.id})

        agreement._compute_mr_count()
        self.assertEqual(
            agreement.mr_count, 1, "Wrong no of Maintenance Request Count!"
        )
