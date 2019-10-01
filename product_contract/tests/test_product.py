# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestProductTemplate(TransactionCase):
    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.service_product = self.env.ref('product.product_product_1')
        self.consu_product = self.env.ref('product.product_product_5')
        self.contract = self.env['contract.template'].create(
            {'name': 'Test'}
        )

    def test_change_is_contract(self):
        """ It should verify that the contract_template_id is removed
        when is_contract is False """
        self.service_product.is_contract = True
        self.service_product.contract_template_id = self.contract.id
        self.service_product.is_contract = False
        self.service_product.product_tmpl_id._change_is_contract()
        self.assertEquals(len(self.service_product.contract_template_id), 0)

    def test_check_contract_product_type(self):
        """
            It should raise ValidationError on change of is_contract to True
            for consu product
        """
        with self.assertRaises(ValidationError):
            self.consu_product.is_contract = True
