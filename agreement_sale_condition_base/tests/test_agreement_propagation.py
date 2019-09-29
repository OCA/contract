# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestAgreementPropagation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.agreement_type = cls.env['agreement.type'].create(
            {'code': 'TST', 'name': 'test'}
        )
        cls.agreement = cls.env['agreement'].create(
            {'name': 'Test Agreement Template',
             'code': 'TST',
             'is_template': 1,
             'agreement_type_id': cls.agreement_type.id,
             }
        )
        cls.product = cls.env['product.product'].create(
            {'name': 'test product',
             'type': 'consu',
             'uom_id': 1,
             }
        )
        cls.partner = cls.env['res.partner'].create(
            {
                'name': 'Test Customer',
                'customer': True,
            }
        )
        cls.sale = cls.env['sale.order'].create(
            {
                'partner_id': cls.partner.id,
                'agreement_type_id': cls.agreement_type.id,
                'order_line': [
                    (0, 0, {
                        'product_id': cls.product.id,
                        'product_uom': cls.product.uom_id.id,
                        'product_uom_qty': 1,
                        'price_unit': 10,
                    }
                    )
                ],
            }
        )

    def test_default_agreement(self):
        self.assertEqual(self.agreement_type.default_agreement_id,
                         self.agreement)

    def test_sale_order_confirm(self):
        sale = self.sale
        sale.onchange_agreement_type()
        self.assertEqual(
            sale.agreement_id.agreement_type_id,
            sale.agreement_type_id
        )
        self.assertNotEqual(
            sale.agreement_id,
            sale.agreement_type_id.default_agreement_id
        )
        self.assertEqual(
            sale.agreement_id.partner_id,
            sale.partner_id
        )
        self.assertTrue(sale.agreement_id.is_sale_agreement)

    def test_agreement_propagation_to_procurement_group(self):
        sale = self.sale
        sale.action_confirm()
        self.assertEqual(
            sale.agreement_id,
            sale.procurement_group_id.agreement_id
        )
