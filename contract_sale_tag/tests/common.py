# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.contract_sale_generation.tests.common import ContractSaleCommon


class ContractSaleTagsCommon(ContractSaleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set Tag 1 and Tag 2 to contract
        # Set Tag 3 to contract 2
        cls.contract_tag_obj = cls.env["contract.tag"]
        vals = {
            "name": "Tag 1",
        }
        cls.tag_1 = cls.contract_tag_obj.create(vals)
        vals = {
            "name": "Tag 2",
        }
        cls.tag_2 = cls.contract_tag_obj.create(vals)

        vals = {
            "name": "Tag 3",
        }
        cls.tag_3 = cls.contract_tag_obj.create(vals)

        cls.contract.tag_ids = cls.tag_1 | cls.tag_2
        cls.contract2.tag_ids = cls.tag_1
