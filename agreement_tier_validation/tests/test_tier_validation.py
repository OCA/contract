# Copyright 2022 Ecosoft Co., Ltd.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.addons.base_tier_validation.tests.common import CommonTierValidation


class TestAgreementTierValidation(CommonTierValidation):
    def test_01_tier_definition_models(self):
        res = self.tier_def_obj._get_tier_validation_model_names()
        self.assertIn("agreement", res)
