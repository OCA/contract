# Copyright 2023 Jaime Millan (<https://xtendoo.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase

from .common import ContractSaleCommon, to_date


class TestContractSale(ContractSaleCommon, TransactionCase):
    def test_contract(self):
        to_date("2020-02-15")
        self.contract_line.price_unit = 100.0
        self.contract.partner_id = self.partner.id
        self.contract.recurring_create_sale()
        self.sale_monthly = self.contract._get_related_sales()
        self.assertEqual(
            self.contract.client_order_ref, self.sale_monthly.client_order_ref
        )
