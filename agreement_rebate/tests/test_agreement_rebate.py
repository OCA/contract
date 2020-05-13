# Copyright 2020 Tecnativa - Carlos Dauden
# Copyright 2020 Tecnativa - Sergio Teruel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import namedtuple
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo import fields
from odoo.exceptions import ValidationError, UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('-at_install', 'post_install')
class TestAgreementRebate(TransactionCase):

    def setUp(self):
        super().setUp()
        self.Partner = self.env['res.partner']
        self.ProductTemplate = self.env['product.template']
        self.Product = self.env['product.product']
        self.ProductCategory = self.env['product.category']
        self.AccountInvoice = self.env['account.invoice']
        self.AccountInvoiceLine = self.env['account.invoice.line']
        self.AccountJournal = self.env['account.journal']
        self.Agreement = self.env['agreement']
        self.AgreementType = self.env['agreement.type']
        self.ProductAttribute = self.env['product.attribute']
        self.ProductAttributeValue = self.env['product.attribute.value']
        self.ProductTmplAttributeValue = self.env[
            'product.template.attribute.value']
        self.AgreementSettlementCreateWiz = self.env[
            'agreement.settlement.create.wiz']
        self.rebate_type = [
            'global',
            'line',
            'section_total',
            'section_prorated',
        ]
        self.category_all = self.env.ref('product.product_category_all')
        self.categ_1 = self.ProductCategory.create({
            'parent_id': self.category_all.id,
            'name': 'Category 1',
        })
        self.categ_2 = self.ProductCategory.create({
            'parent_id': self.category_all.id,
            'name': 'Category 2',
        })
        self.product_1 = self.Product.create({
            'name': 'Product test 1',
            'categ_id': self.categ_1.id,
            'list_price': 1000.00,
        })
        self.product_2 = self.Product.create({
            'name': 'Product test 2',
            'categ_id': self.categ_2.id,
            'list_price': 2000.00,
        })
        # Create a product with variants
        self.product_attribute = self.ProductAttribute.create({
            'name': 'Test',
            'create_variant': 'always',
        })
        self.product_attribute_value_test_1 = self.ProductAttributeValue.create({
            'name': 'Test v1',
            'attribute_id': self.product_attribute.id,
        })
        self.product_attribute_value_test_2 = self.ProductAttributeValue.create({
            'name': 'Test v2',
            'attribute_id': self.product_attribute.id,
        })
        self.product_template = self.ProductTemplate.create({
            'name': 'Product template with variant test',
            'type': 'consu',
            'list_price': 100.0,
            'attribute_line_ids': [
                (0, 0, {
                    'attribute_id': self.product_attribute.id,
                    'value_ids': [
                        (4, self.product_attribute_value_test_1.id),
                        (4, self.product_attribute_value_test_2.id),
                    ],
                }),
            ],
        })
        self.partner_1 = self.Partner.create({
            'name': 'partner test rebate 1',
            'customer': True,
            'ref': 'TST-001',
        })
        self.partner_2 = self.Partner.create({
            'name': 'partner test rebate 2',
            'customer': True,
            'ref': 'TST-002',
        })
        self.invoice_partner_1 = self.create_invoice(self.partner_1)
        self.invoice_partner_2 = self.create_invoice(self.partner_2)
        self.agreement_type = self.AgreementType.create({
            'name': 'Rebate',
            'journal_type': 'sale',
        })
        # self.create_agreements_rebate(self.partner_1)
        # self.create_agreements_rebate(self.partner_2)

    # Create some invoices for partner
    def create_invoice(self, partner):
        invoice = self.AccountInvoice.create({
            'name': "Test Customer Invoice",
            'journal_id': self.AccountJournal.search(
                [('type', '=', 'sale')])[0].id,
            'partner_id': partner.id,
        })
        products = (self.product_template.product_variant_ids +
                    self.product_1 + self.product_2)
        self.create_invoice_line(invoice, products)
        return invoice

    def create_invoice_line(self, invoice, products):
        val_list = []
        for product in products:
            inv_line = self.AccountInvoiceLine.with_context(
                force_company=self.env.user.company_id.id,
            ).new({
                'invoice_id': invoice.id,
                'product_id': product.id,
                'uom_id': product.uom_id.id,
            })
            inv_line._onchange_product_id()

            # Assign distinct prices for product with variants
            if product == self.product_template.product_variant_ids[0]:
                inv_line.price_unit = 300.00
            if product == self.product_template.product_variant_ids[1]:
                inv_line.price_unit = 500.00

            val_list.append(inv_line._convert_to_write(inv_line._cache))
        self.AccountInvoiceLine.create(val_list)

    # Create Agreements rebates for customers for all available types
    def create_agreements_rebate(self, rebate_type, partner):
        agreement = self.Agreement.create({
            'rebate_type': rebate_type,
            'name': 'A discount {} for all lines for {}'.format(
                rebate_type, partner.name),
            'code': 'R-{}-{}'.format(rebate_type, partner.ref),
            'partner_id': partner.id,
            'agreement_type_id': self.agreement_type.id,
            'rebate_discount': 10,
            'rebate_line_ids': [
                (0, 0, {
                    'rebate_target': 'product',
                    'rebate_product_ids': [(6, 0, self.product_1.ids)],
                    'rebate_discount': 20
                }),
                (0, 0, {
                    'rebate_target': 'product',
                    'rebate_product_ids': [
                        (6, 0,
                         self.product_template.product_variant_ids[0].ids)],
                    'rebate_discount': 30
                }),
                (0, 0, {
                    'rebate_target': 'product_tmpl',
                    'rebate_product_tmpl_ids': [
                        (6, 0, self.product_2.product_tmpl_id.ids)],
                    'rebate_discount': 40,
                }),
                (0, 0, {
                    'rebate_target': 'category',
                    'rebate_category_ids': [
                        (6, 0, self.category_all.ids)],
                    'rebate_discount': 40,
                }),
            ],
            'rebate_section_ids': [
                        (0, 0, {
                            'amount_from': 0.00,
                            'amount_to': 100.00,
                            'rebate_discount': 10,
                        }),
                        (0, 0, {
                            'amount_from': 100.01,
                            'amount_to': 300.00,
                            'rebate_discount': 20,
                        }),
                        (0, 0, {
                            'amount_from': 300.01,
                            'amount_to': 6000.00,
                            'rebate_discount': 30,
                        }),
                    ],
            })
        # agreement_line = agreement_global.copy({
        #     'rebate_type': 'line',
        #     'code': 'R-L-{}'.format(partner.ref),
        #     'name': 'A discount for every line for {}'.format(partner.name),
        # })
        # agreement_section_total = agreement_global.copy({
        #     'rebate_type': 'section_total',
        #     'code': 'R-S-T-{}'.format(partner.ref),
        #     'name': 'Compute total and apply discount '
        #             'rule match for {}'.format(partner.name),
        # })
        # agreement_section_prorated = agreement_global.copy({
        #     'rebate_type': 'section_prorated',
        #     'code': 'R-S-P-{}'.format(partner.ref),
        #     'name': 'Compute multi-dicounts by sections amount '
        #             'for {}'.format(partner.name),
        # })
        return agreement

    def test_create_settlement_wo_filters(self):
        # Invoice Lines:
        # Product template variants: 300, 500
        # Product 1: 1000
        # Product 2: 2000
        # Total by invoice: 3800 amount invoiced

        # Global rebate without filters
        agreement_global = self.create_agreements_rebate(
            'global', self.partner_1)
        agreement_global.rebate_line_ids = False
        settlement_wiz = self.env['agreement.settlement.create.wiz'].create({})
        settlements = settlement_wiz.action_create_settlement()
        self.assertEqual(len(settlements), 1)
        self.assertEqual(settlements.amount_invoiced, 3800)
        self.assertEqual(settlements.amount_rebate, 380)

        # Line rebate without filters
        agreement = self.create_agreements_rebate(
            'line', self.partner_1)
        agreement.rebate_line_ids = False
        settlement_wiz = self.env['agreement.settlement.create.wiz'].create({})
        settlements = settlement_wiz.action_create_settlement()
        self.assertEqual(len(settlements), 0)

        # section_total rebate without filters
        agreement = self.create_agreements_rebate(
            'section_total', self.partner_1)
        agreement.rebate_line_ids = False
        settlement_wiz = self.env['agreement.settlement.create.wiz'].create({})
        settlements = settlement_wiz.action_create_settlement()
        self.assertEqual(len(settlements), 1)
        self.assertEqual(settlements.amount_invoiced, 3800)
        self.assertEqual(settlements.amount_rebate, 1140)

        # section_prorated rebate without filters
        agreement = self.create_agreements_rebate(
            'section_prorated', self.partner_1)
        agreement.rebate_line_ids = False
        settlement_wiz = self.env['agreement.settlement.create.wiz'].create({})
        settlements = settlement_wiz.action_create_settlement()
        self.assertEqual(len(settlements), 1)
        self.assertEqual(settlements.amount_invoiced, 3800)
        self.assertAlmostEqual(settlements.amount_rebate, 1120.00, 2)

    def test_create_settlement_products_filters(self):
        # Invoice Lines:
        # Product template variants: 300, 500
        # Product 1: 1000
        # Product 2: 2000
        # Total by invoice: 3800 amount invoiced

        for rebate_type in self.rebate_type:
            agreement = self.create_agreements_rebate(
                rebate_type, self.partner_1)
            agreement.rebate_line_ids = [(5, 0), (0, 0, {
                'rebate_target': 'product',
                'rebate_product_ids': [(6, 0, self.product_1.ids)],
                'rebate_discount': 20,
            })]
            settlement_wiz = self.AgreementSettlementCreateWiz.create({})
            settlements = settlement_wiz.action_create_settlement()
            self.assertEqual(len(settlements), 1)
            self.assertEqual(settlements.amount_invoiced, 1000)
            if rebate_type == 'global':
                self.assertEqual(settlements.amount_rebate, 100)
            if rebate_type == 'line':
                self.assertEqual(settlements.amount_rebate, 200)
            if rebate_type == 'section_total':
                self.assertEqual(settlements.amount_rebate, 300)
            if rebate_type == 'section_prorated':
                self.assertAlmostEqual(settlements.amount_rebate, 280, 2)
