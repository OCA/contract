# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.contract.tests.test_contract import TestContractBase
from odoo.addons.queue_job.tests.common import JobMixin


class TestContractAutoValidate(TestContractBase, JobMixin):
    @classmethod
    def setUpClass(cls):
        super(TestContractAutoValidate, cls).setUpClass()
        cls.contract3 = cls.contract2.copy()

    def _get_related_invoices(self, contracts):
        return (
            self.env['account.invoice.line']
            .search(
                [
                    (
                        'contract_line_id',
                        'in',
                        contracts.mapped('contract_line_ids.id'),
                    )
                ]
            )
            .mapped('invoice_id')
        )

    def test_contract_invoice_auto_validate(self):
        contracts = self.contract2
        invoice = contracts._recurring_create_invoice()
        self.assertEqual(invoice.state, 'open')
