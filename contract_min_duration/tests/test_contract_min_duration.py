# Copyright 2025 bosd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestContractMinDuration(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})
        cls.product = cls.env["product.product"].create(
            {"name": "Test Service", "type": "service"}
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Min Duration Contract",
                "partner_id": cls.partner.id,
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2025-01-01",
                "min_contract_end_date": "2025-06-30",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.id,
                            "name": "Service",
                            "quantity": 1,
                            "price_unit": 100,
                            "recurring_interval": 1,
                            "recurring_rule_type": "monthly",
                            "date_start": "2025-01-01",
                        },
                    )
                ],
            }
        )

    def test_end_date_enforcement_on_write(self):
        """Test that setting date_end earlier than min_contract_end_date
        forces it to min date."""
        # Try to terminate on Feb 28th (early)
        self.contract.write({"date_end": "2025-02-28"})

        # Expectation: date_end should be auto-extended to 2025-06-30
        self.assertEqual(
            self.contract.date_end,
            fields.Date.to_date("2025-06-30"),
            "Contract end date should be extended to minimum end date",
        )

    def test_end_date_later_than_min(self):
        """Test that setting date_end later than min_contract_end_date
        works as normal."""
        # Terminate on Dec 31st (allowed)
        self.contract.write({"date_end": "2025-12-31"})

        self.assertEqual(
            self.contract.date_end,
            fields.Date.to_date("2025-12-31"),
            "Contract end date should be respected if after minimum",
        )

    def test_change_min_date_triggers_check(self):
        """Test that increasing min_contract_end_date updates existing date_end."""
        # Set an end date that is valid FOR NOW
        self.contract.write({"date_end": "2025-08-31"})  # Initial min is June

        # Now extend the minimum requirement to September
        self.contract.write({"min_contract_end_date": "2025-09-30"})

        self.assertEqual(
            self.contract.date_end,
            fields.Date.to_date("2025-09-30"),
            "Existing end date should be updated when minimum constraint increases",
        )

    def test_end_date_enforcement_on_create(self):
        """Test that creating a contract with date_end < min_date is corrected."""
        contract = self.env["contract.contract"].create(
            {
                "name": "Test Create Contract",
                "partner_id": self.partner.id,
                "date_start": "2025-01-01",
                "min_contract_end_date": "2025-06-30",
                "date_end": "2025-03-31",  # Invalid end date
            }
        )
        self.assertEqual(
            contract.date_end,
            fields.Date.to_date("2025-06-30"),
            "Contract end date should be extended to minimum on creation",
        )
