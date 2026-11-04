# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.fields import Command

from odoo.addons.base.tests.common import BaseCommon


class TestContractDate(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = cls.env["product.product"].create(
            {"name": "Service", "type": "service"}
        )
        cls._create_contract()
        cls._create_contract_2()
        cls._create_contract_3()

    @classmethod
    @freeze_time("2026-10-02")
    def _create_contract(cls):
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "test",
                "partner_id": cls.partner.id,
                "recurring_interval": 1,
                "recurring_invoicing_type": "post-paid",
                "recurring_rule_type": "monthly",
                "fixed_invoice_day_number": 10,
                "contract_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "quantity": 1.0,
                        }
                    )
                ],
            }
        )

    @classmethod
    @freeze_time("2026-10-12")
    def _create_contract_2(cls):
        cls.contract_2 = cls.env["contract.contract"].create(
            {
                "name": "test",
                "partner_id": cls.partner.id,
                "recurring_interval": 1,
                "recurring_invoicing_type": "post-paid",
                "recurring_rule_type": "monthly",
                "fixed_invoice_day_number": 10,
                "contract_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "quantity": 1.0,
                        }
                    )
                ],
            }
        )

    @classmethod
    @freeze_time("2026-10-12")
    def _create_contract_3(cls):
        cls.contract_3 = cls.env["contract.contract"].create(
            {
                "name": "test",
                "partner_id": cls.partner.id,
                "recurring_interval": 1,
                "recurring_invoicing_type": "post-paid",
                "recurring_rule_type": "monthly",
                "contract_line_ids": [
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "name": cls.product.name,
                            "quantity": 1.0,
                        }
                    )
                ],
            }
        )

    @freeze_time("2026-11-01")
    def test_invoice_date(self):
        self.assertEqual(
            fields.Date.from_string("2026-10-10"),
            self.contract.next_fixed_invoice_date,
        )

    @freeze_time("2026-11-12")
    def test_invoice_date_over(self):
        self.contract_2.recurring_next_date = "2026-11-12"
        self.assertEqual(
            fields.Date.from_string("2026-12-10"),
            self.contract_2.next_fixed_invoice_date,
        )
        move = self.contract_2.recurring_create_invoice()
        self.assertTrue(move)
        self.assertEqual(
            move.date,
            fields.Date.from_string("2026-12-10"),
        )

    @freeze_time("2026-11-01")
    def test_invoice_date_without(self):
        self.assertFalse(
            self.contract_3.next_fixed_invoice_date,
        )

    def test_constraint(self):
        with self.assertRaises(ValidationError):
            self.contract.fixed_invoice_day_number = 32

        with self.assertRaises(ValidationError):
            self.contract.fixed_invoice_day_number = -1
