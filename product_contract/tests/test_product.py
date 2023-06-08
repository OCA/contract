# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestProductTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                no_reset_password=True,
            )
        )
        cls.service_product = cls.env.ref("product.product_product_1")
        cls.consu_product = cls.env.ref("product.product_product_5")
        cls.contract = cls.env["contract.template"].create({"name": "Test"})

    def test_change_is_contract(self):
        """It should verify that the property_contract_template_id
        field value is removed for all the companies when
        is_contract is set to False"""
        self.service_product.is_contract = True
        self.service_product.property_contract_template_id = self.contract.id
        self.service_product.is_contract = False
        self.assertEqual(len(self.service_product.property_contract_template_id), 0)

    def test_check_contract_product_type(self):
        """
        It should raise ValidationError on change of is_contract to True
        for consu product
        """
        with self.assertRaises(ValidationError):
            self.consu_product.is_contract = True
