# Copyright 2023 Foodles (http://www.foodles.co/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractDiscounts(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.contract4 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract4",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": True,
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
                            "discount_fixed": 48,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2018-02-15",
                            "recurring_next_date": "2018-02-22",
                        },
                    )
                ],
            }
        )

    def test_invoice_lines_discount_fixed(self):
        invoice = self.contract4.recurring_create_invoice()
        self.assertEquals(invoice.invoice_line_ids.discount_fixed, 48)
        self.assertEquals(invoice.invoice_line_ids.discount, 0)
