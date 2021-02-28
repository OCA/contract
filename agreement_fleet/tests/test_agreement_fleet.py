# Copyright (C) 2021 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestAgreementFleet(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAgreementFleet, cls).setUpClass()
        cls.vehicle_model = cls.env.ref('fleet.model_corsa')

        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@test.com',
        })
        cls.agreement = cls.env['agreement'].create({
            'name': 'Test Agreement',
            'partner_id': cls.partner.id,
        })
        cls.vehicle = cls.env['fleet.vehicle'].create({
            'name': 'Test Fleet Vehicle',
            'model_id': cls.vehicle_model.id,
            'license_plate': 'Test License Plate',
            'agreement_id': cls.agreement.id,
        })

    def test_compute_vehicle_count(self):
        self.agreement._compute_vehicle_count()
        self.assertEqual(
            self.agreement.vehicle_count, 1)

    def test_action_view_vehicle(self):
        result = self.agreement.action_view_vehicle()
        self.assertEqual(result['res_id'], self.vehicle.id)
