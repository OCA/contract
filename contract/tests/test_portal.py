# Copyright 2020 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import odoo.tests
from odoo import http


@odoo.tests.tagged("post_install", "-at_install")
class TestContractPortal(odoo.tests.HttpCase):
    def test_tour(self):
        partner = self.env['res.partner'].create({
            'name': 'partner test contract'
        })
        contract = self.env['contract.contract'].create(
            {
                'name': 'Test Contract',
                'partner_id': partner.id
            }
        )
        user_portal = self.env.ref('base.demo_user0')
        contract.message_subscribe(partner_ids=user_portal.partner_id.ids)
        self.phantom_js(
            "/",
            "odoo.__DEBUG__.services['web_tour.tour'].run('contract_portal_tour')",
            "odoo.__DEBUG__.services['web_tour.tour'].tours.contract_portal_tour.ready",
            login="portal",
        )
        # Contract access
        self.authenticate('portal', 'portal')
        http.root.session_store.save(self.session)
        url_contract = "/my/contracts/%s?access_token=%s" % (
            contract.id, contract.access_token
        )
        self.assertEqual(self.url_open(url=url_contract).status_code, 200)
        contract.message_unsubscribe(partner_ids=user_portal.partner_id.ids)
        self.assertEqual(self.url_open(url=url_contract).status_code, 200)
