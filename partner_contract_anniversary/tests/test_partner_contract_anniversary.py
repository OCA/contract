# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

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

    def _create_partner_line_starting(self, date_start):
        partner = self.env["res.partner"].create({"name": "Leap Day Partner"})
        contract = self.contract.copy(
            {"partner_id": partner.id, "contract_line_ids": False}
        )
        line_vals = dict(
            self.line_vals,
            contract_id=contract.id,
            date_start=date_start,
            recurring_next_date=date_start,
        )
        self.env["contract.line"].create(line_vals)
        return partner

    def test_anniversary_date_29_february_non_leap_year(self):
        """A contract started on 29/02 has its anniversary on 28/02 on a
        non leap year."""
        with freeze_time("2025-06-01"):
            partner = self._create_partner_line_starting("2020-02-29")
            self.assertEqual(
                partner.first_contract_line_start_date, to_date("2020-02-29")
            )
            self.assertEqual(partner.contract_anniversary_date, to_date("2025-02-28"))

    def test_anniversary_date_29_february_leap_year(self):
        """A contract started on 29/02 keeps its anniversary on 29/02 on a
        leap year."""
        with freeze_time("2028-06-01"):
            partner = self._create_partner_line_starting("2020-02-29")
            self.assertEqual(partner.contract_anniversary_date, to_date("2028-02-29"))
