# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class Setup(TransactionCase):

    def setUp(self):
        super(Setup, self).setUp()

        self.ContractCheckout = self.env['contract.checkout']
        self.ContractTemp = self.env['contract.temp']

        self.order_1 = self.env.ref(
            'website_sale_contract.sale_order_1'
        )
        self.line_1 = self.env.ref(
            'website_sale_contract.sale_order_line_1'
        )
        self.line_2 = self.env.ref(
            'website_sale_contract.sale_order_line_2'
        )
        self.line_3 = self.env.ref(
            'website_sale_contract.sale_order_line_3'
        )
        self.line_4 = self.env.ref(
            'website_sale_contract.sale_order_line_4'
        )

    def _build_test_contract_checkout(self, order=None):
        if not order:
            order = self.env.ref(
                'website_sale_contract.sale_order_1'
            )
        Checkout = self.env['contract.checkout']
        return Checkout.get_or_create_contract_checkout(order)

    def _create_contract_temp(self, order_line=None):
        if not order_line:
            order_line = self.env.ref(
                'website_sale_contract.sale_order_line_1',
            )
        ContractTemp = self.env['contract.temp']
        return ContractTemp.create
