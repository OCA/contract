# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields

from odoo.addons.contract.tests.test_contract import TestContractBase
from odoo.addons.queue_job.tests.common import JobMixin


class TestContractLineQueueJob(TestContractBase, JobMixin):
    @classmethod
    def setUpClass(cls):
        super(TestContractLineQueueJob, cls).setUpClass()
        cls.contract3 = cls.contract2.copy()

    def test_contract_renew_queue_job_1(self):
        """Only one line, task is run without delay"""
        line = self.contract2.mapped("contract_line_ids")
        line.date_end = fields.Date.today()
        res = line.renew()
        self.assertTrue(line.date_end < res.date_start)

    def test_contract_renew_queue_job_2(self):
        """Two lines, two jobs are created."""
        contracts = self.contract2 | self.contract3
        lines = contracts.mapped("contract_line_ids")
        job_counter = self.job_counter()
        lines.renew()
        self.assertEqual(job_counter.count_created(), len(lines))
