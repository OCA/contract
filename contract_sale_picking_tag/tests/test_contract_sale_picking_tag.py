# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import SavepointCase

from .common import ContractSalePickingTagsCommon


class TestContractTagsSale(ContractSalePickingTagsCommon, SavepointCase):
    def test_contract_picking_tag(self):
        self.contract.recurring_create_sale()

        sale = self.contract._get_related_sales()
        self.assertEquals(
            self.contract.tag_ids,
            sale.contract_tag_ids,
        )
        sale.action_confirm()
        self.assertEqual(sale.picking_ids.contract_tag_ids, self.contract.tag_ids)
