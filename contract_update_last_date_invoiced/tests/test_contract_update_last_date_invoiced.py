# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.addons.base.tests.common import BaseCommon


class TestContractLine(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
            }
        )
        cls.contract_line = cls.env["contract.line"].create(
            {
                "name": "Test Contract Line",
                "contract_id": cls.contract.id,
                "date_start": date(2024, 2, 1),
                "last_date_invoiced": date(2024, 2, 1),
                "recurring_next_date": date(2024, 3, 1),
            }
        )
        cls.wizard = cls.env["contract.update.last.date.invoiced"].create(
            {
                "contract_line_id": cls.contract_line.id,
                "last_date_invoiced": "2024-02-15",
                "recurring_next_date": "2024-03-15",
            }
        )

    def test_action_update_last_date_invoiced(self):
        action = self.contract_line.action_update_last_date_invoiced()
        self.assertEqual(
            action["context"]["default_recurring_next_date"],
            self.contract_line.recurring_next_date,
        )

    def test_update_last_date_invoiced(self):
        new_last_date = date(2024, 2, 15)  # Convert to date
        new_next_date = date(2024, 3, 15)
        self.contract_line._update_last_date_invoiced(new_last_date, new_next_date)
        self.assertEqual(self.contract_line.last_date_invoiced, new_last_date)
        self.assertEqual(self.contract_line.recurring_next_date, new_next_date)

    def test_update_last_date_invoiced_wizard(self):
        self.wizard.update_last_date_invoiced()
        self.assertEqual(self.contract_line.last_date_invoiced, date(2024, 2, 15))
        self.assertEqual(self.contract_line.recurring_next_date, date(2024, 3, 15))
