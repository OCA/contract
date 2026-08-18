# Copyright 2026 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from dateutil.relativedelta import relativedelta

from odoo.addons.contract.tests.test_contract import TestContractBase
from odoo.addons.queue_job.tests.common import JobMixin


class TestContractInvoicing(TestContractBase, JobMixin):
    """
    Tests for forced date on manual contract invoicing
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["ir.config_parameter"].sudo().set_param("contract.queue.job", "true")

    def test_contract_manual_invoice_force_date(self):
        job_counter = self.job_counter()
        tomorrow = self.today + relativedelta(days=1)
        wizard = self.env["contract.manually.create.invoice"].create(
            {"invoice_date": self.today}
        )
        wizard.invoice_date_forced = tomorrow
        wizard.create_invoice_queued()
        self.assertEqual(job_counter.count_created(), 2)
        self.perform_jobs(job_counter)
        invoices = (
            self.env["account.move.line"]
            .search(
                [
                    (
                        "contract_line_id",
                        "in",
                        self.contract.contract_line_ids.ids,
                    )
                ]
            )
            .mapped("move_id")
        )
        for invoice in invoices:
            self.assertEqual(invoice.invoice_date, tomorrow)
