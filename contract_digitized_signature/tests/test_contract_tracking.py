# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestContractSignatureTracking(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestContractSignatureTracking, cls).setUpClass()
        # Simple 1x1 transparent base64 encoded GIF
        cls.image = 'R0lGODlhAQABAAAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=='

    def test_contract_signature_tracking(self):
        self.contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'customer_signature': self.image,
        })
        message = self.env['mail.message'].search([
            ('res_id', '=', self.contract.id)
        ], order='id desc', limit=1)
        self.assertIn('Signature has been created.', message.body)
