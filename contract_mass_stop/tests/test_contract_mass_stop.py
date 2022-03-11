# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from freezegun import freeze_time

from odoo import fields

from odoo.addons.contract.tests.test_contract import TestContractBase


class TestContractMassStop(TestContractBase):
    @classmethod
    @freeze_time("2018-02-15")
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.stop_wizard = cls.env["contract.mass.stop"]
        cls.contract4 = cls.contract3.copy()

    @classmethod
    def _create_stop_wizard(cls, contracts, **values):
        cls.wizard = cls.stop_wizard.with_context(active_ids=contracts.ids).create(
            values
        )

    @freeze_time("2018-02-15")
    def test_contract_mass_stop(self):
        # Test on contract 3 and 4 - start at 2018-02-15
        # Interrupt from 2018-04-01 to 2018-05-14
        # Create invoices
        # Check if march ones are created
        # Create invoices
        # Check if next invoices are generated from 2018-05-15 (gap)
        self.contract3.line_recurrence = True
        self.contract4.line_recurrence = True
        self.contract3.recurring_create_invoice()
        invoices = self.contract3._get_related_invoices()
        past_invoices = invoices
        self.assertEqual(
            self.contract3.recurring_next_date, fields.Date.to_date("2018-03-15")
        )
        self.assertEqual(fields.Date.to_date("2018-02-15"), invoices.invoice_date)
        self.contract4.recurring_create_invoice()
        invoices4 = self.contract4._get_related_invoices()
        past_invoices4 = invoices4
        self.assertEqual(
            self.contract4.recurring_next_date, fields.Date.to_date("2018-03-15")
        )
        self.assertEqual(fields.Date.to_date("2018-02-15"), invoices4.invoice_date)
        values = {
            "date_start": "2018-04-01",
            "date_end": "2018-05-14",
        }
        self._create_stop_wizard((self.contract3 | self.contract4), **values)

        self.wizard.doit()
        self.contract3.recurring_create_invoice()
        invoices = self.contract3._get_related_invoices() - past_invoices
        past_invoices |= invoices
        self.assertEqual(fields.Date.to_date("2018-03-15"), invoices.invoice_date)

        self.contract3.recurring_create_invoice()
        invoices = self.contract3._get_related_invoices() - past_invoices
        self.assertEqual(fields.Date.to_date("2018-05-15"), invoices.invoice_date)

        self.contract4.recurring_create_invoice()
        invoices4 = self.contract4._get_related_invoices() - past_invoices4
        past_invoices4 |= invoices4
        self.assertEqual(fields.Date.to_date("2018-03-15"), invoices4.invoice_date)

        self.contract4.recurring_create_invoice()
        invoices4 = self.contract4._get_related_invoices() - past_invoices4
        self.assertEqual(fields.Date.to_date("2018-05-15"), invoices4.invoice_date)

    @freeze_time("2018-02-15")
    def test_contract_mass_stop_global(self):
        # Test with no recurrence on lines
        # Test on contract 3 and 4 - start at 2018-02-15
        # Interrupt from 2018-04-01 to 2018-05-14
        # Create invoices
        # Check if march ones are created
        # Create invoices
        # Check if next invoices are generated from 2018-05-15 (gap)
        self.contract3.recurring_create_invoice()
        invoices = self.contract3._get_related_invoices()
        past_invoices = invoices
        self.assertEqual(
            self.contract3.recurring_next_date, fields.Date.to_date("2018-03-15")
        )
        self.assertEqual(fields.Date.to_date("2018-02-15"), invoices.invoice_date)
        self.contract4.recurring_create_invoice()
        invoices4 = self.contract4._get_related_invoices()
        past_invoices4 = invoices4
        self.assertEqual(
            self.contract4.recurring_next_date, fields.Date.to_date("2018-03-15")
        )
        self.assertEqual(fields.Date.to_date("2018-02-15"), invoices4.invoice_date)
        values = {
            "date_start": "2018-04-01",
            "date_end": "2018-05-14",
        }
        self._create_stop_wizard((self.contract3 | self.contract4), **values)

        self.wizard.doit()
        self.contract3.recurring_create_invoice()
        invoices = self.contract3._get_related_invoices() - past_invoices
        past_invoices |= invoices
        self.assertEqual(fields.Date.to_date("2018-03-15"), invoices.invoice_date)

        self.contract3.recurring_create_invoice()
        invoices = self.contract3._get_related_invoices() - past_invoices
        self.assertEqual(fields.Date.to_date("2018-05-15"), invoices.invoice_date)

        self.contract4.recurring_create_invoice()
        invoices4 = self.contract4._get_related_invoices() - past_invoices4
        past_invoices4 |= invoices4
        self.assertEqual(fields.Date.to_date("2018-03-15"), invoices4.invoice_date)

        self.contract4.recurring_create_invoice()
        invoices4 = self.contract4._get_related_invoices() - past_invoices4
        self.assertEqual(fields.Date.to_date("2018-05-15"), invoices4.invoice_date)
