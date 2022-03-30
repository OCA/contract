# Copyright 2022 Ecosoft (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import Form, TransactionCase


class TestContractInvoicePlan(TransactionCase):
    def setUp(self):
        super(TestContractInvoicePlan, self).setUp()
        # Create a Contract
        self.Contract = self.env["contract.contract"]
        self.ContractInvoicePlan = self.env["contract.create.invoice.plan"]
        self.test_partner = self.env.ref("base.res_partner_12")
        self.test_product1 = self.env.ref("product.product_product_2")
        self.test_product2 = self.env.ref("product.product_product_7")

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
                            "price_unit": 5000,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.test_product2.name,
                            "product_id": self.test_product2.id,
                            "quantity": 1,
                            "price_unit": 5000,
                        },
                    ),
                ],
            }
        )

    def test_invoice_plan(self):
        ctx = {
            "active_id": self.test_contract.id,
            "active_ids": [self.test_contract.id],
            "all_remain_invoices": True,
        }
        # Create invoice plan
        with Form(self.ContractInvoicePlan) as p:
            p.num_installment = 5
        contract_plan = p.save()
        contract_plan.with_context(ctx).contract_create_invoice_plan()
        # Change plan, so that the 1st installment is 1000 and 5th is 3000
        self.assertEqual(len(self.test_contract.invoice_plan_ids), 5)
        self.test_contract.invoice_plan_ids[0].amount = 1000
        self.test_contract.invoice_plan_ids[4].amount = 3000
        contract_create = self.env["contract.make.planned.invoice"].create({})
        contract_create.with_context(ctx).create_invoices_by_plan()
        self.assertEqual(
            self.test_contract.amount_total,
            sum(self.test_contract._get_related_invoices().mapped("amount_untaxed")),
        )

    def test_unlink_invoice_plan(self):
        ctx = {
            "active_id": self.test_contract.id,
            "active_ids": [self.test_contract.id],
        }
        with Form(self.ContractInvoicePlan) as p:
            p.num_installment = 5
        plan = p.save()
        plan.with_context(ctx).contract_create_invoice_plan()
        # Remove it
        self.test_contract.remove_invoice_plan()
        self.assertFalse(self.test_contract.invoice_plan_ids)
