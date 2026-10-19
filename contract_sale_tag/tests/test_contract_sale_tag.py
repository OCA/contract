# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase

from .common import ContractSaleTagsCommon


class TestContractTagsSale(ContractSaleTagsCommon, TransactionCase):
    def test_contract(self):
        self.contract.recurring_create_sale()

        sale = self.contract._get_related_sales()
        self.assertEqual(
            self.contract.tag_ids,
            sale.contract_tag_ids,
        )
