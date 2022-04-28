# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase
from odoo.addons.queue_job.tests.common import JobMixin


class TestContractQueueJob(TestContractBase, JobMixin):
    @classmethod
    def setUpClass(cls):
        super(TestContractQueueJob, cls).setUpClass()
        cls.contract3 = cls.contract2.copy()

    def _get_related_invoices(self, contracts):
        return (
            self.env["account.move.line"]
            .search(
                [
                    (
                        "contract_line_id",
                        "in",
                        contracts.mapped("contract_line_ids.id"),
                    )
                ]
            )
            .mapped("move_id")
        )

    def test_contract_queue_job(self):
        contracts = self.contract2 | self.contract3
        job_counter = self.job_counter()
        invoices = contracts._recurring_create_invoice()
        self.assertFalse(invoices)
        invoices = self._get_related_invoices(contracts)
        self.assertFalse(invoices)
        self.assertEqual(job_counter.count_created(), 2)
        self.perform_jobs(job_counter)
        invoices = self._get_related_invoices(contracts)
        self.assertEqual(len(invoices), 2)

    def test_contract_queue_job_1(self):
        contracts = self.contract2
        job_counter = self.job_counter()
        count_all_jobs = job_counter.count_all()
        self.assertEqual(job_counter.count_all(), count_all_jobs)
        invoices_res = contracts._recurring_create_invoice()
        self.assertTrue(invoices_res)
        invoices = self._get_related_invoices(contracts)
        self.assertEqual(invoices_res, invoices)

    def test_contract_queue_job_2(self):
        contracts = self.contract2 | self.contract3
        job_counter = self.job_counter()
        wizard = self.env["contract.manually.create.invoice"].create(
            {"invoice_date": self.today, "contract_type": "purchase"}
        )
        wizard.create_invoice()
        invoices = self._get_related_invoices(contracts)
        self.assertFalse(invoices)
        self.assertEqual(job_counter.count_created(), 2)
        self.perform_jobs(job_counter)
        invoices = self._get_related_invoices(contracts)
        self.assertEqual(len(invoices), 2)
