# coding: utf-8
# © 2018 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestSale(TransactionCase):

    def test_partner_invoice(self):
        """ Check Agreement set the right invoice partner """
        # import pdb; pdb.set_trace()
        invoice_part = (self.env.ref(
            'agreement_sale_partner_invoice.sale_partner_agreement')
            .partner_invoice_id)
        self.assertEqual(
            invoice_part, self.env.ref('base.res_partner_1'))
