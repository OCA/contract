# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import tagged

from odoo.addons.contract.tests.test_contract import TestContract


def to_date(date):
    return fields.Date.to_date(date)


@tagged("post_install", "-at_install")
class TestContractPartnerAnniversary(TestContract):
    def test_check_anniversary_date(self):
        expected_first_contractln_date = min(
            self.partner.contract_ids.contract_line_ids.mapped("date_start")
        )
        self.assertEqual(expected_first_contractln_date, to_date("2018-01-01"))
        expected_anniversary = fields.datetime(fields.datetime.today().year, 1, 1)
        self.assertEqual(
            self.partner.contract_anniversary_date, expected_anniversary.date()
        )
