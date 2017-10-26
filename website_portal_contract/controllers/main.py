# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import http
from odoo.http import request

from odoo.addons.website_portal_sale.controllers.main import website_account


class WebsiteAccount(website_account):

    @http.route()
    def account(self, **kw):
        response = super(WebsiteAccount, self).account(**kw)
        contracts = request.env['account.analytic.account']._search_contracts()
        response.qcontext.update({
            'contract_count': len(contracts),
        })
        return response


class WebsiteContract(http.Controller):

    @http.route(
        ['/my/contracts'],
        type='http',
        auth='user',
        website=True,
    )
    def portal_my_contracts(self):
        account_mod = request.env['account.analytic.account']
        values = {
            'user': request.env.user,
            'contracts': account_mod._search_contracts(),
        }
        return request.render(
            'website_portal_contract.portal_my_contracts',
            values,
        )

    @http.route(
        ['/contract/<model("account.analytic.account"):contract>'],
        type='http',
        auth='user',
        website=True
    )
    def portal_contract(self, contract):
        action = request.env.ref(
            'contract.action_account_analytic_overdue_all'
        )
        values = {
            'user': request.env.user,
            'contract': contract,
            'action': action.id,
        }
        return request.render(
            'website_portal_contract.website_contract',
            values,
        )

    @http.route(
        ["/contract/template/"
         "<model('account.analytic.contract.template'):contract>"],
        type='http',
        auth='user',
        website=True,
    )
    def template_view(self, contract, **kwargs):
        values = {'template': contract}
        return request.render(
            'website_portal_contract.website_contract_template',
            values,
        )
