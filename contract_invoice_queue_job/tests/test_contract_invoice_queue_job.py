# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from math import ceil

from odoo import fields

from odoo.addons.contract.tests.test_contract import TestContractBase

from ..models.res_config_settings import CONTRACT_INVOICING_CHUNK_SIZE


class TestContractAutoValidate(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Contract = cls.env["contract.contract"]
        cls.chunk_size = 20
        cls.env["ir.config_parameter"].sudo().set_param(
            CONTRACT_INVOICING_CHUNK_SIZE, cls.chunk_size
        )
        contract = cls.Contract.create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": True,
            }
        )
        contracts = contract
        for _i in range(50):
            contracts |= contract.copy()
        cls.contracts = contracts

    def test_contract_manually_create_invoice_batch(self):
        """
        Test manual invoice batch creation
        """
        now = fields.Datetime.now()
        wizard = self.env["contract.manually.create.invoice"].create(
            {"invoice_date": self.today}
        )
        wizard.create_invoice_batch()
        jobs = self.env["queue.job"].search(
            [
                ("model_name", "=", "contract.contract"),
                ("method_name", "=", "_recurring_create_invoice"),
                ("date_created", ">=", now),
                ("name", "ilike", "Manual Batch Invoice Contracts"),
            ]
        )
        num_expected_jobs = ceil(wizard.contract_to_invoice_count / self.chunk_size)
        self.assertEqual(len(jobs), num_expected_jobs)

    def test_cron_recurring_create_invoice(self):
        """
        Test automated invoice batch creation
        """
        now = fields.Datetime.now()
        domain = self.Contract._get_contracts_to_invoice_domain()
        to_invoice_contracts = self.Contract.search(domain)
        self.env["contract.contract"].cron_recurring_create_invoice()
        jobs = self.env["queue.job"].search(
            [
                ("model_name", "=", "contract.contract"),
                ("method_name", "=", "_recurring_create_invoice"),
                ("date_created", ">=", now),
                ("name", "ilike", "Automated Batch Invoice Contracts"),
            ]
        )
        num_expected_jobs = ceil(len(to_invoice_contracts) / self.chunk_size)
        self.assertEqual(len(jobs), num_expected_jobs)
