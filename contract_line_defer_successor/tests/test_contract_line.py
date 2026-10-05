# Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.base.tests.common import BaseCommon
from odoo.addons.contract.tests.test_contract import TestContractBase


class Test(BaseCommon, TestContractBase):
    """
    Tests for contract.line
    """

    def test_deferred_line_actions_not_allowed(self):
        """A deferred line disallows every successor/stop/cancel action."""
        line = self.acct_line
        line.is_auto_renew = False
        self.assertTrue(line.is_stop_allowed)
        self.assertTrue(line.is_cancel_allowed)

        line.is_deferred = True

        self.assertFalse(line.is_plan_successor_allowed)
        self.assertFalse(line.is_stop_plan_successor_allowed)
        self.assertFalse(line.is_stop_allowed)
        self.assertFalse(line.is_cancel_allowed)
        self.assertFalse(line.is_un_cancel_allowed)
