# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import date

from odoo.tests.common import TransactionCase


class TestContractServiceDates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Product", "type": "service"}
        )
        journal = cls.env["account.journal"].search(
            [("type", "=", "sale"), ("company_id", "=", cls.env.company.id)],
            limit=1,
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "journal_id": journal.id,
                "contract_type": "sale",
                "line_recurrence": True,
            }
        )

    def _create_line(self, date_start, date_end=None, **extra):
        vals = {
            "contract_id": self.contract.id,
            "product_id": self.product.id,
            "name": "Test line",
            "quantity": 1.0,
            "price_unit": 100.0,
            "date_start": date_start,
            "recurring_next_date": date_start,
            "recurring_rule_type": "monthly",
            "recurring_invoicing_type": "pre-paid",
            "recurring_interval": 1,
        }
        if date_end is not None:
            vals["date_end"] = date_end
        vals.update(extra)
        return self.env["contract.line"].create(vals)

    def test_create_copies_dates(self):
        """service dates are initialised from date_start / date_end on create."""
        line = self._create_line(date(2025, 1, 1), date(2025, 12, 31))
        self.assertEqual(line.service_start_date, date(2025, 1, 1))
        self.assertEqual(line.service_end_date, date(2025, 12, 31))

    def test_create_no_end_date(self):
        """service_end_date is False when date_end is not set."""
        line = self._create_line(date(2025, 1, 1))
        self.assertEqual(line.service_start_date, date(2025, 1, 1))
        self.assertFalse(line.service_end_date)

    def test_create_explicit_service_dates_preserved(self):
        """Explicitly supplied service dates are not overwritten on create."""
        line = self._create_line(
            date(2025, 1, 1),
            date(2025, 12, 31),
            service_start_date=date(2025, 3, 1),
            service_end_date=date(2025, 9, 30),
        )
        self.assertEqual(line.service_start_date, date(2025, 3, 1))
        self.assertEqual(line.service_end_date, date(2025, 9, 30))

    def test_write_date_start_syncs_service_start(self):
        """Modifying date_start updates service_start_date when still in sync."""
        line = self._create_line(date(2025, 1, 1), date(2025, 12, 31))
        line.write({"date_start": date(2025, 2, 1)})
        self.assertEqual(line.service_start_date, date(2025, 2, 1))

    def test_write_date_end_syncs_service_end(self):
        """Modifying date_end updates service_end_date when still in sync."""
        line = self._create_line(date(2025, 1, 1), date(2025, 12, 31))
        line.write({"date_end": date(2025, 6, 30)})
        self.assertEqual(line.service_end_date, date(2025, 6, 30))

    def test_write_date_start_does_not_overwrite_decoupled_service_start(self):
        """Modifying date_start leaves service_start_date alone when decoupled."""
        line = self._create_line(date(2025, 1, 1), date(2025, 12, 31))
        # Manually decouple service_start_date
        line.write({"service_start_date": date(2025, 3, 1)})
        # Now change date_start — service_start_date must not follow
        line.write({"date_start": date(2025, 2, 1)})
        self.assertEqual(line.service_start_date, date(2025, 3, 1))

    def test_write_date_end_does_not_overwrite_decoupled_service_end(self):
        """Modifying date_end leaves service_end_date alone when decoupled."""
        line = self._create_line(date(2025, 1, 1), date(2025, 12, 31))
        # Manually decouple service_end_date
        line.write({"service_end_date": date(2025, 9, 30)})
        # Now change date_end — service_end_date must not follow
        line.write({"date_end": date(2026, 12, 31)})
        self.assertEqual(line.service_end_date, date(2025, 9, 30))
