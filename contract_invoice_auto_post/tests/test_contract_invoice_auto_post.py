# Copyright 2023 Xtendoo - Carlos Camacho
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestContractBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner test contract",
                "email": "demo@demo.com",
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 2",
                "partner_id": cls.partner.id,
                "line_recurrence": True,
                "generation_type": "invoice",
                "auto_post": "at_date",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_1.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": cls.product_1.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2018-02-15",
                            "recurring_next_date": "2018-02-22",
                        },
                    )
                ],
            }
        )

    def test_invoice_auto_post_at_date(self):
        invoice = self.contract.recurring_create_invoice()
        self.assertEqual(invoice.auto_post, "at_date")
