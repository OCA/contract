# Copyright 2026 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestContractSettings(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.discount_group = cls.env.ref("contract.group_discount_per_contract_line")

    @property
    def internal_users(self):
        return self.env.ref("base.group_user")

    def _set_discounts(self, enabled):
        self.env["res.config.settings"].create(
            {"group_discount_per_contract_line": enabled}
        ).execute()

    def test_discounts_are_shown_by_default(self):
        """An install that never touched the setting keeps showing discounts."""
        self.assertIn(self.discount_group, self.internal_users.implied_ids)

    def test_discounts_can_be_hidden_and_shown_again(self):
        """Unticking the setting takes the discount column away, ticking restores it."""
        self._set_discounts(False)
        self.assertNotIn(self.discount_group, self.internal_users.implied_ids)
        self._set_discounts(True)
        self.assertIn(self.discount_group, self.internal_users.implied_ids)
