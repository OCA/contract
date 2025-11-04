# Copyright 2020 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import Command, http
from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger


@tagged("post_install", "-at_install")
class TestContractPortal(HttpCase):
    @mute_logger(
        "odoo.addons.contract.tests.test_portal.TestContractPortal.test_tour.browser"
    )
    def test_tour(self):
        partner = self.env["res.partner"].create({"name": "partner test contract"})
        contract = self.env["contract.contract"].create(
            {"name": "Test Contract", "partner_id": partner.id}
        )
        portal_group = self.env.ref("base.group_portal")
        user_portal = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "partner_id": partner.id,
                    "login": "portal",
                    "password": "portal",
                    "signature": "Mr Demo Portal",
                    "group_ids": [Command.clear(), Command.link(portal_group.id)],
                }
            )
        )
        contract.message_subscribe(partner_ids=user_portal.partner_id.ids)
        ready_code = (
            "(function(){"
            "var t=window.odoo&&odoo.tour&&odoo.tour.tours&&"
            "odoo.tour.tours.contract_portal_tour;"
            "if(!t||!t.steps){return true;}"
            "for(var i=0;i<t.steps.length;i++){"
            "  var s=t.steps[i];"
            "  if(s&&s.trigger&&"
            "s.trigger.indexOf('/my/contracts')!==-1){"
            "s.expectUnloadPage=true;"
            "}"
            "}"
            "return true;"
            "})()"
        )
        self.start_tour("/", "contract_portal_tour", login="portal", ready=ready_code)
        # Contract access
        self.authenticate("portal", "portal")
        http.root.session_store.save(self.session)
        url_contract = (
            f"/my/contracts/{contract.id}?access_token={contract.access_token}"
        )
        self.assertEqual(self.url_open(url=url_contract).status_code, 200)
        contract.message_unsubscribe(partner_ids=user_portal.partner_id.ids)
        self.assertEqual(self.url_open(url=url_contract).status_code, 200)
