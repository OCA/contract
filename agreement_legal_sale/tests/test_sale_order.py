# Copyright 2021 Ecosoft Co., Ltd (http://ecosoft.co.th)
# Copyright 2021 Sergio Teruel - Tecnativa
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    def setUp(self):
        super().setUp()
        self.test_customer = self.env["res.partner"].create({"name": "TestCustomer"})
        self.agreement_type = self.env["agreement.type"].create(
            {
                "name": "Test Agreement Type",
                "domain": "sale",
            }
        )
        self.analytic_plan = self.env["account.analytic.plan"].create(
            {"name": "Test Plan"}
        )
        self.test_account_analytic_account = self.env[
            "account.analytic.account"
        ].create({"name": "Test Analytic Account", "plan_id": self.analytic_plan.id})
        self.test_agreement_template = self.env["agreement"].create(
            {
                "name": "TestAgreementTemplate",
                "description": "Test Template",
                "special_terms": "Test Template",
                "is_template": True,
                "partner_id": self.test_customer.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today() + timedelta(days=365),
                "analytic_account_id": self.test_account_analytic_account.id,
            }
        )
        self.test_agreement_template_no_analytic_account_id = self.env[
            "agreement"
        ].create(
            {
                "name": "TestAgreementTemplate A",
                "description": "Test Template",
                "special_terms": "Test Template",
                "is_template": True,
                "partner_id": self.test_customer.id,
                "start_date": fields.Date.today(),
                "end_date": fields.Date.today() + timedelta(days=365),
            }
        )
        self.test_product = self.env["product.product"].create({"name": "TestProduct"})
        self.test_sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.test_customer.id,
                "agreement_template_id": self.test_agreement_template.id,
                "date_order": fields.Date.today(),
                "order_line": [
                    (0, 0, {"display_type": "line_section", "name": "Test section"}),
                    (0, 0, {"display_type": "line_note", "name": "Test note"}),
                    (
                        0,
                        0,
                        {"product_id": self.test_product.id, "product_uom_qty": 1.0},
                    ),
                ],
            }
        )
        self.test_product_templ_is_serviceprofile = self.env["product.template"].create(
            {
                "name": "TestProductA",
                "type": "service",
                "service_tracking": "serviceprofile",
            }
        )
        self.test_product_is_serviceprofile = self.env["product.product"].create(
            {
                "name": "TestProductA",
                "product_tmpl_id": self.test_product_templ_is_serviceprofile.id,
            }
        )
        self.test_sale_order_is_serviceprofile = self.env["sale.order"].create(
            {
                "partner_id": self.test_customer.id,
                "agreement_template_id": self.test_agreement_template.id,
                "date_order": fields.Date.today(),
                "order_line": [
                    (0, 0, {"display_type": "line_section", "name": "Test section"}),
                    (0, 0, {"display_type": "line_note", "name": "Test note"}),
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product_is_serviceprofile.id,
                            "product_uom_qty": 1.0,
                        },
                    ),
                ],
            }
        )

    # TEST 01: Test _action_confirm method
    def test_action_confirm(self):
        sale_order = self.test_sale_order
        sale_order._action_confirm()
        agreement = self.env["agreement"].search([("sale_id", "=", sale_order.id)])
        self.assertEqual(
            agreement.sale_id.id,
            sale_order.id,
        )

        # Test 02: is_serviceprofile Product
        is_serviceprofile_so = self.test_sale_order_is_serviceprofile
        is_serviceprofile_so._action_confirm()
        self.assertEqual(
            self.env["agreement.serviceprofile"].search_count(
                [("agreement_id.sale_id", "=", is_serviceprofile_so.id)]
            ),
            1,
        )
        agreement = self.env["agreement"].search(
            [("sale_id", "=", is_serviceprofile_so.id)]
        )
        self.assertEqual(
            agreement.sale_id.id,
            is_serviceprofile_so.id,
        )
