# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase

from odoo.addons.contract_sale_generation.tests.common import ContractSaleCommon


class TestContractSaleDeliveryZone(ContractSaleCommon, SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delivery_zone_a = cls.env["partner.delivery.zone"].create(
            {"name": "Delivery Zone A", "code": "10"}
        )
        cls.delivery_zone_b = cls.env["partner.delivery.zone"].create(
            {"name": "Delivery Zone B", "code": "10"}
        )
        cls.contract.partner_delivery_zone_id = cls.delivery_zone_a

    def test_contract_sale_delivery_zone(self):
        self.contract.recurring_create_sale()
        sale = self.contract._get_related_sales()
        self.assertEqual(
            sale.delivery_zone_id,
            self.delivery_zone_a,
        )
        sale.delivery_zone_id = self.delivery_zone_b
        self.assertEqual(
            sale.delivery_zone_id,
            self.delivery_zone_b,
        )
