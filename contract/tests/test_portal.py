# Copyright 2020 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import http
from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestContractPortal(HttpCase, BaseCommon):
    @mute_logger(
        "odoo.addons.contract.tests.test_portal.TestContractPortal.test_tour.browser"
    )
    def test_tour(self):
        partner = self.env["res.partner"].create({"name": "partner test contract"})
        contract = self.env["contract.contract"].create(
            {"name": "Test Contract", "partner_id": partner.id}
        )
        user_portal = self._create_new_portal_user(
            partner_id=partner.id, login="portal_contract", password="portal_contract"
        )
        self.start_tour("/", "contract_portal_tour", login="portal_contract")
        # Contract access
        self.authenticate("portal_contract", "portal_contract")
        http.root.session_store.save(self.session)
        url_contract = (
            f"/my/contracts/{contract.id}?access_token={contract.access_token}"
        )
        self.assertEqual(self.url_open(url=url_contract).status_code, 200)
        contract.message_unsubscribe(partner_ids=user_portal.partner_id.ids)
        self.assertEqual(self.url_open(url=url_contract).status_code, 200)
