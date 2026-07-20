# Copyright 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon

from ..hooks import pre_init_hook


@tagged("post_install", "-at_install")
class TestContractPaymentInit(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_data2 = cls.setup_other_company(name="Test contract payment mode")
        cls.company2 = cls.company_data2["company"]
        cls.Contract = cls.env["contract.contract"]
        PaymentMethod = cls.env["account.payment.method"]
        PaymentMode = cls.env["account.payment.mode"]
        cls.payment_method = PaymentMethod.create(
            {
                "name": "Test Payment Method",
                "code": "Test",
                "payment_type": "inbound",
            }
        )
        cls.payment_method_outbound = PaymentMethod.create(
            {
                "name": "Test Payment Method 2",
                "code": "Test2",
                "payment_type": "outbound",
            }
        )
        cls.payment_mode_outbound = PaymentMode.create(
            {
                "name": "Test payment mode 3",
                "payment_method_id": cls.payment_method_outbound.id,
                "bank_account_link": "variable",
                "company_id": cls.company2.id,
            }
        )
        cls.payment_mode = PaymentMode.create(
            {
                "name": "Test payment mode",
                "payment_method_id": cls.payment_method.id,
                "bank_account_link": "variable",
                "company_id": cls.company.id,
            }
        )
        cls.payment_mode2 = PaymentMode.create(
            {
                "name": "Test payment mode 2",
                "payment_method_id": cls.payment_method.id,
                "bank_account_link": "variable",
                "company_id": cls.company2.id,
            }
        )
        cls.specific_payment_mode = cls.payment_mode2.copy(
            default={"name": "Specific payment mode"}
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test contract partner"})
        cls.partner_without_payment_mode = cls.env["res.partner"].create(
            {"name": "Test contract partner 2"}
        )
        cls.partner.with_company(cls.company).write(
            {"customer_payment_mode_id": cls.payment_mode.id}
        )
        cls.partner.with_company(cls.company2).write(
            {
                "customer_payment_mode_id": cls.payment_mode2.id,
                "supplier_payment_mode_id": cls.payment_mode_outbound.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Custom Service",
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "sale_ok": True,
            }
        )
        cls.contract = cls.Contract.create(
            {"name": "Maintenance of Servers", "partner_id": cls.partner.id}
        )

    def test_pre_init_hook(self):
        contract2 = self.Contract.create(
            {
                "name": "Test contract",
                "partner_id": self.partner.id,
                "company_id": self.company2.id,
            }
        )
        contract_with_payment_mode = self.env["contract.contract"].create(
            {
                "name": "Test contract",
                "partner_id": self.partner.id,
                "payment_mode_id": self.specific_payment_mode.id,
                "company_id": self.company2.id,
            }
        )
        # partner_without_payment_mode has no payment mode set,
        # so the contract should not have a payment mode either
        contract_without_payment_mode = self.Contract.create(
            {
                "name": "Test contract",
                "partner_id": self.partner_without_payment_mode.id,
            }
        )
        contract_supplier = self.Contract.create(
            {
                "name": "Test contract",
                "partner_id": self.partner.id,
                "contract_type": "purchase",
                "company_id": self.company2.id,
            }
        )
        self.assertEqual(self.contract.payment_mode_id, self.payment_mode)
        self.assertEqual(contract2.payment_mode_id, self.payment_mode2)
        self.assertEqual(
            contract_with_payment_mode.payment_mode_id, self.specific_payment_mode
        )
        self.assertFalse(contract_without_payment_mode.payment_mode_id)
        self.assertEqual(contract_supplier.payment_mode_id, self.payment_mode_outbound)
        self.contract.payment_mode_id = False
        contract2.payment_mode_id = False
        contract_supplier.payment_mode_id = False
        self.Contract.flush_model(["payment_mode_id"])
        pre_init_hook(self.env)
        self.Contract.invalidate_model(["payment_mode_id"])
        self.assertEqual(self.contract.payment_mode_id, self.payment_mode)
        self.assertEqual(contract2.payment_mode_id, self.payment_mode2)
        self.assertEqual(
            contract_with_payment_mode.payment_mode_id, self.specific_payment_mode
        )
        self.assertFalse(contract_without_payment_mode.payment_mode_id)
        self.assertEqual(contract_supplier.payment_mode_id, self.payment_mode_outbound)

    def test_contract_and_invoices(self):
        self.contract.write({"partner_id": self.partner.id})
        self.assertEqual(
            self.contract.payment_mode_id,
            self.contract.partner_id.customer_payment_mode_id,
        )
        self.contract.write(
            {
                "line_recurrence": True,
                "contract_type": "sale",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2018-01-15",
                "contract_line_ids": [
                    Command.create(
                        {
                            "product_id": self.product.id,
                            "name": "Database Administration 25",
                            "quantity": 2.0,
                            "uom_id": self.product.uom_id.id,
                            "price_unit": 200.0,
                        },
                    )
                ],
            }
        )
        self.contract.recurring_create_invoice()
        new_invoice = self.contract._get_related_invoices()
        self.assertTrue(new_invoice)
        self.assertEqual(new_invoice.partner_id, self.contract.partner_id)
        self.assertEqual(new_invoice.payment_mode_id, self.contract.payment_mode_id)
        self.assertEqual(len(new_invoice.ids), 1)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.contract.payment_mode_id, new_invoice.payment_mode_id)
