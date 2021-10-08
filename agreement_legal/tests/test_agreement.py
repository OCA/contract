# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.addons.agreement.tests import test_agreement


class TestAgreement(test_agreement.TestAgreement):
    def setUp(self):
        super().setUp()

    def test_action_create_new_version(self):
        self.agreement.create_new_version()
        self.assertEqual(self.agreement.state, "draft")
        self.assertEqual(len(self.agreement.previous_version_agreements_ids), 1)
