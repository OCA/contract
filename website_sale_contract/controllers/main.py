# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route(
        ['/shop/payment'],
        type='http',
        auth='public',
        method='GET',
        website=True,
    )
    def payment(self, **post):

        Website = request.website.with_context(request.env.context)
        order = Website.sale_get_order()

        redirection = self.checkout_redirection(order)

        if redirection:
            return redirection

        sale_lines = order.order_line.filtered(
            lambda s: s.product_id.is_contract
        )

        if not sale_lines:
            return super(WebsiteSale, self).payment(**post)

        checkout = request.env['contract.checkout'].search([
            ('order_id', '=', order.id)
        ])

        if checkout:
            accepted_contracts = checkout.temp_contract_ids.filtered(
                lambda s: s.accepted,
            )
            if len(accepted_contracts) == len(checkout.temp_contract_ids):
                return super(WebsiteSale, self).payment(**post)

        return request.redirect(
            '/shop/checkout/contract'
        )

    @http.route(
        ['/shop/cart/update'],
        type='http',
        auth='public',
        methods=['POST'],
        website=True,
        csrf=False,
    )
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        self._check_detach_contract_checkout(int(product_id))
        return super(WebsiteSale, self).cart_update(
            product_id=product_id,
            add_qty=1,
            set_qty=0,
            kw=kw,
        )

    @http.route(
        ['/shop/cart/update_json'],
        type='json',
        auth='public',
        methods=['POST'],
        website=True,
        csrf=False,
    )
    def cart_update_json(self, product_id, line_id=None, add_qty=None,
                         set_qty=None, display=True):
        self._check_detach_contract_checkout(int(product_id))
        return super(WebsiteSale, self).cart_update_json(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            display=display,
        )

    def _check_detach_contract_checkout(self, product_id):
        """ Removes contract checkout from order if product is a contract """
        order = request.website.sale_get_order()
        product = request.env['product.product'].browse(product_id)
        if order and product.is_contract:
            request.env['contract.checkout'].search_checkout_detach_order(
                order=order,
            )


class SaleContract(http.Controller):

    @http.route(
        ['/shop/checkout/contract'],
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
    )
    def contract_step(self):
        website = request.website.with_context(request.env.context)
        order = website.sale_get_order()

        ContractCheckout = request.env['contract.checkout']
        contract_wizard = \
            ContractCheckout.get_or_create_contract_checkout(order)

        first_contract = contract_wizard.temp_contract_ids[0]

        return request.redirect(first_contract.website_url)

    @http.route(
        ['/shop/checkout/contract/<int:contract_id>/<token>'],
        type='http',
        auth='public',
        methods=['GET'],
        website=True,
    )
    def show_contract(self, contract_id, token, message_id=None):

        domain = [('id', '=', contract_id),
                  ('access_token', '=', token)]

        contract = request.env['contract.temp'].search(domain)

        if not contract:
            return request.render('website.404')

        website = request.website.with_context(request.env.context)
        order = website.sale_get_order()

        if contract.contract_checkout_id.order_id != order:
            return request.render('website.403')

        prev_unsigned = \
            contract.get_previous_unsigned_contracts()

        if prev_unsigned:
            contract = prev_unsigned[0]
            return request.redirect(
                '/shop/checkout/contract/%s/%s?message_id=%s' % (
                    contract.id, contract.access_token, 2,
                )
            )

        values = {
            'user': request.env.user,
            'website': website,
            'contract': contract,
            'message': message_id and int(message_id) or False,
            'wizard': contract.contract_checkout_id,
            'contract_template': contract.contract_template_id,
        }
        return request.render(
            'website_sale_contract.contract_checkout',
            values,
        )

    @http.route(
        ['/shop/checkout/contract/accept'],
        type='json',
        auth='public',
        methods=['POST'],
        website=True,
    )
    def accept_contract(self, contract_id, token, signatory_name,
                        signature_image):

        contract = request.env['contract.temp'].browse(contract_id)

        res = {
            'message_id': 1,
        }

        if not contract:
            return res

        website = request.website.with_context(request.env.context)
        order = website.sale_get_order()

        conditions = (
            token == contract.access_token,
            contract.contract_checkout_id.order_id == order,
            signatory_name,
            signature_image,
        )

        if all(conditions):
            res['message_id'] = 3
            contract.write({
                'signature_image': signature_image,
                'signatory_name': signatory_name,
            })

        return res
