# Copyright 2017 Pesol (<http://pesol.es>)
# Copyright 2017 Angel Moya <angel.moya@pesol.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestInvoiceContract(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestInvoiceContract, cls).setUpClass()

        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "partner 1 test contract",
                "email": "demo1@demo.com",
            }
        )
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "partner 2 test contract",
                "email": "demo2@demo.com",
            }
        )
        cls.contract1 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 1",
                "partner_id": cls.partner1.id,
                "line_recurrence": False,
                "contract_type": "sale",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2022-01-01",
                "free_invoice_date": False,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": False,
                            "name": "Product 1",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )
        cls.contract2 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 1",
                "partner_id": cls.partner2.id,
                "line_recurrence": False,
                "contract_type": "sale",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2022-01-01",
                "free_invoice_date": True,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": False,
                            "name": "Product 1",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    ),
                ],
            }
        )

    def test01_create_invoice_with_date(self):
        """Testing contract invoice generation with default date"""
        self.contract1.recurring_create_invoice()
        invoices = self.contract1._get_related_invoices()
        self.assertTrue(invoices[0].invoice_date)

    def test02_create_invoice_without_date(self):
        """Testing contract invoice generation with 'free invoice date'
        field functionality"""
        self.contract2.recurring_create_invoice()
        invoices = self.contract2._get_related_invoices()
        self.assertFalse(invoices[0].invoice_date)
