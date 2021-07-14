# Copyright (C) 2021 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo import fields


class TestAgreementMrp(common.TransactionCase):
    def setUp(self):
        super(TestAgreementMrp, self).setUp()

        self.agreement_obj = self.env["agreement"]
        self.mrp_production_obj = self.env["mrp.production"]
        self.agreement_type_id = self.env["agreement.type"].create(
            {"name": "Test Agreement Type", "active": True}
        )
        self.product = self.env.ref(
            "mrp.product_product_computer_desk_bolt_product_template"
        )

    def test_fieldservice_purchase(self):
        agreement_vals = {
            "name": "Test Agreement",
            "agreement_type_id": self.agreement_type_id.id,
            "description": "Test Agreement",
            "start_date": fields.Date.today(),
            "end_date": fields.Date.today(),
        }
        agreement = self.agreement_obj.create(agreement_vals)

        mrp_production_vals = {
            "product_id": self.product.product_variant_id.id,
            "agreement_id": agreement.id,
            "product_uom_id": self.product.uom_id.id,
        }
        mrp_production_new = self.mrp_production_obj.new(mrp_production_vals)
        mrp_production_vals.update(
            mrp_production_new.default_get(mrp_production_new._fields)
        )

        self.mrp_production_obj.create(mrp_production_vals)

        agreement._compute_mo_count()
        self.assertEqual(agreement.mo_count, 1, "Wrong no of MO's!")
