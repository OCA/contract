# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api
from odoo.tests import common


class TestContractLine(common.SavepointCase):

    @api.multi
    def test_contract_line(self):
        partner = self.env.ref('base.res_partner_2')
        product = self.env.ref('product.product_product_2')
        template = self.env['account.analytic.contract'].create({
            'name': 'Test Template',
            'recurring_invoices': True,
            'recurring_rule_type': 'yearly',
            'recurring_interval': 1})
        self.env['account.analytic.contract.line'].create({
            'analytic_account_id': template.id,
            'product_id': product.id,
            'name': 'Template Line',
            'quantity': 1,
            'uom_id': product.uom_id.id,
            'price_unit': 90})
        contract = self.env['account.analytic.account'].create({
            'name': 'Test Contract',
            'contract_template_id': template.id,
            'partner_id': partner.id,
            'recurring_invoices': True,
            'recurring_rule_type': 'yearly',
            'recurring_interval': 1,
            'date_start': '2016-02-15',
            'recurring_next_date': '2016-02-29'})
        contract_line = self.env['account.analytic.invoice.line'].create({
            'analytic_account_id': contract.id,
            'product_id': product.id,
            'name': 'Services from #START# to #END#',
            'quantity': 1,
            'uom_id': product.uom_id.id,
            'price_unit': 100})
        self.assertEqual(contract_line.contract_id.id, contract.id)
        self.assertEqual(contract_line.partner_id.id, contract.partner_id.id)
        self.assertEqual(contract_line.date_start, contract.date_start)
