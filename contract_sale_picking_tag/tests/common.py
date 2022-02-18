# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import Form

from odoo.addons.contract_sale_tag.tests.common import ContractSaleTagsCommon


class ContractSalePickingTagsCommon(ContractSaleTagsCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # We replace the product used by a stockable one
        cls.product_10 = cls.env.ref("product.product_product_10")
        with Form(cls.contract.contract_line_ids[0]) as line_form:
            line_form.product_id = cls.product_10
