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
        """ It should verify that the property_contract_template_id
        field value is removed for all the companies when
        is_contract is set to False """
        self.service_product.is_contract = True
        self.service_product.property_contract_template_id = self.contract.id
        self.service_product.is_contract = False
        self.assertEquals(len(
            self.service_product.property_contract_template_id), 0)

    def test_check_contract_product_type(self):
        """
            It should raise ValidationError on change of is_contract to True
            for consu product
        """
        with self.assertRaises(ValidationError):
            self.consu_product.is_contract = True

    def test_check_contract_template_write(self):
        """It should not be possible to write a contract on 'not a contract'."""
        template_values = {"name": "Name", "is_contract": False}
        not_a_contract = self.env["product.template"].create(template_values)
        with self.assertRaises(ValidationError):
            not_a_contract.property_contract_template_id = self.contract

    def test_check_contract_template_create(self):
        """It should not be possible to create a 'not a contract' with a contract."""
        template_values = {"name": "Name", "is_contract": False}
        template_values["property_contract_template_id"] = self.contract.id
        with self.assertRaises(ValidationError):
            self.env["product.template"].create(template_values)
