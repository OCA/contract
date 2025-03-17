# Copyright 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2017 Tecnativa - David Vidal
# Copyright 2023 Tecnativa - Carolina Fernandez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.models.account_payment_method import AccountPaymentMethod
from odoo.addons.base.tests.common import BaseCommon

from ..hooks import post_init_hook


@tagged("post_install", "-at_install")
class TestContractPaymentInit(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        Method_get_payment_method_information = (
            AccountPaymentMethod._get_payment_method_information
        )

        def _get_payment_method_information(self):
            res = Method_get_payment_method_information(self)
            res["Test"] = {"mode": "multi", "domain": [("type", "=", "bank")]}
            return res

        with patch.object(
            AccountPaymentMethod,
            "_get_payment_method_information",
            _get_payment_method_information,
        ):
            cls.payment_method = cls.env["account.payment.method"].create(
                {
                    "name": "Test Payment Method",
                    "code": "Test",
                    "payment_type": "inbound",
                }
            )

        cls.payment_mode = cls.env["account.payment.mode"].create(
            {
                "name": "Test payment mode",
                "active": True,
                "payment_method_id": cls.payment_method.id,
                "bank_account_link": "variable",
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test contract partner",
                "customer_payment_mode_id": cls.payment_mode.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {
                "name": "Custom Service",
                "type": "service",
                "uom_id": cls.env.ref("uom.product_uom_hour").id,
                "uom_po_id": cls.env.ref("uom.product_uom_hour").id,
                "sale_ok": True,
            }
        )
        cls.contract = cls.env["contract.contract"].create(
            {"name": "Maintenance of Servers", "partner_id": cls.partner.id}
        )
        company = cls.env.ref("base.main_company")
        cls.journal = cls.env["account.journal"].create(
            {
                "name": "Sale Journal - Test",
                "code": "HRTSJ",
                "type": "sale",
                "company_id": company.id,
            }
        )

    def test_post_init_hook(self):
        contract = self.env["contract.contract"].create(
            {
                "name": "Test contract",
                "partner_id": self.partner.id,
                "payment_mode_id": self.payment_mode.id,
            }
        )
        self.assertEqual(contract.payment_mode_id, self.payment_mode)

        contract.payment_mode_id = False
        self.assertEqual(contract.payment_mode_id.id, False)

        post_init_hook(self.env)
        self.assertEqual(contract.payment_mode_id, self.payment_mode)

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
