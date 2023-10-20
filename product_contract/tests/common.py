# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV
# Copyright 2018 Foodles
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase


class CommonProductContractSaleOrderCase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                no_reset_password=True,
            )
        )
        cls.product1 = cls.env.ref("product.product_product_1")
        cls.product2 = cls.env.ref("product.product_product_2")
        cls.sale = cls.env.ref("sale.sale_order_2")
        cls.contract_template1 = cls.env["contract.template"].create(
            {"name": "Template 1"}
        )
        cls.contract_template2 = cls.env["contract.template"].create(
            {
                "name": "Template 2",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": cls.product2.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "yearly",
                            "recurring_interval": 1,
                        },
                    )
                ],
            }
        )
        cls.product1.with_company(cls.sale.company_id).write(
            {
                "is_contract": True,
                "default_qty": 12,
                "recurring_rule_type": "monthlylastday",
                "recurring_invoicing_type": "post-paid",
                "property_contract_template_id": cls.contract_template1.id,
            }
        )
        cls.product2.with_company(cls.sale.company_id).write(
            {
                "is_contract": True,
                "property_contract_template_id": cls.contract_template2.id,
            }
        )
        cls.order_line1 = cls.sale.order_line.filtered(
            lambda l: l.product_id == cls.product1
        )

        cls.order_line1.date_start = "2018-01-01"
        cls.order_line1.product_uom_qty = 12
        cls.order_line1.product_id_change()
        cls.order_line2 = cls.sale.order_line.filtered(
            lambda l: l.product_id == cls.product2
        )
        cls.order_line2.product_id_change()
