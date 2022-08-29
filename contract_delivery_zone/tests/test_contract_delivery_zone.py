# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import SavepointCase


class TestContractBase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.delivery_zone = cls.env["partner.delivery.zone"].create(
            {"name": "Delivery Zone", "code": "10"}
        )
        cls.delivery_zone_b = cls.env["partner.delivery.zone"].create(
            {"name": "Delivery Zone B", "code": "20"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Contract Delivery Zone Contact",
                "email": "demo@demo.com",
                "delivery_zone_id": cls.delivery_zone.id,
            }
        )

    def test_contract_delivery_zone(self):
        # Create a contract with partner
        # A default delivery zone should come from him
        # Change the zone, it should be well changed
        with Form(self.env["contract.contract"]) as contract_form:
            contract_form.name = "Contract"
            contract_form.partner_id = self.partner
        contract = contract_form.save()
        self.assertEqual(contract.partner_delivery_zone_id, self.delivery_zone)

        with Form(contract) as contract_form:
            contract_form.partner_delivery_zone_id = self.delivery_zone_b

        self.assertEqual(contract.partner_delivery_zone_id, self.delivery_zone_b)
