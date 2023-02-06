# Copyright 2023 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase


@tagged("post_install", "-at_install")
class TestInvoicePlanSelection(TransactionCase):
    def setUp(self):
        super(TestInvoicePlanSelection, self).setUp()
        self.ContractInvoicePlan = self.env["contract.create.invoice.plan"]
        self.Contract = self.env["contract.contract"]
        self.MakeInvoice = self.env["contract.make.planned.invoice"]
        self.test_partner = self.env.ref("base.res_partner_12")
        self.test_product1 = self.env.ref("product.product_product_2")
        self.test_product2 = self.env.ref("product.product_product_7")
        self.test_base_on_all_line = self.env.ref(
            "contract_invoice_plan_selection.apply_on_all_product_line"
        )

        self.test_contract = self.env["contract.contract"].create(
            {
                "name": "My Contract",
                "partner_id": self.test_partner.id,
                "use_invoice_plan": True,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.test_product1.name,
                            "product_id": self.test_product1.id,
                            "quantity": 1,
                            "price_unit": 500,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.test_product2.name,
                            "product_id": self.test_product2.id,
                            "quantity": 1,
                            "price_unit": 1000,
                        },
                    ),
                ],
            }
        )

    def test_create_invoice_by_manual_selection(self):
        # Check next date in contract line is not False
        self.assertTrue(self.test_contract.contract_line_ids[0].recurring_next_date)
        ctx = {
            "active_id": self.test_contract.id,
            "active_ids": [self.test_contract.id],
        }
        # Create contract plan
        with Form(self.ContractInvoicePlan) as p:
            p.num_installment = 2  # 50% each
        contract_plan = p.save()
        contract_plan.with_context(**ctx).contract_create_invoice_plan()
        invoice_plan = self.test_contract.invoice_plan_ids
        # Create 1st installment
        with Form(self.MakeInvoice.with_context(**ctx)) as f:
            f.next_bill_method = "manual"
            f.installment_id = invoice_plan[0]
            f.apply_method_id = self.test_base_on_all_line
        wizard = f.save()
        # Test line quantity
        self.assertEqual(wizard.invoice_qty_line_ids.mapped("quantity"), [0.5, 0.5])
        self.assertTrue(wizard.valid_amount)
        wizard.create_invoice_by_selection()
        self.assertEqual(sum(invoice_plan[0].invoice_ids.mapped("amount_untaxed")), 750)
        # Create 2nd installment
        with Form(self.MakeInvoice.with_context(**ctx)) as f:
            f.next_bill_method = "manual"
            f.installment_id = invoice_plan[1]
            f.apply_method_id = self.test_base_on_all_line
        wizard = f.save()
        self.assertEqual(wizard.invoice_qty_line_ids.mapped("quantity"), [0.5, 0.5])
        # Manually set all qty to 0.25 instead of 0.5
        wizard.invoice_qty_line_ids.write({"quantity": 0.25})
        self.assertFalse(wizard.valid_amount)
        wizard.create_invoice_by_selection()
        self.assertEqual(sum(invoice_plan[1].invoice_ids.mapped("amount_untaxed")), 375)
