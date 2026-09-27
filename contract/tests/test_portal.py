# Copyright 2020 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import http
from odoo.tests import HttpCase, tagged
from odoo.tools import mute_logger
from odoo.tools.safe_eval import safe_eval, time

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

    def test_portal_contract_report(self):
        """The sidebar "View Details" button renders the contract report."""
        partner = self.env["res.partner"].create({"name": "partner test report"})
        contract = self.env["contract.contract"].create(
            {"name": "Reported Contract", "partner_id": partner.id}
        )
        self._create_new_portal_user(
            partner_id=partner.id, login="portal_report", password="portal_report"
        )
        self.authenticate("portal_report", "portal_report")
        http.root.session_store.save(self.session)
        response = self.url_open(
            url=f"/my/contracts/{contract.id}"
            f"?access_token={contract.access_token}&report_type=html"
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recurring Items", response.text)
        # The PDF variant names the downloaded file after the contract, and
        # names it the same way the backend Print action does.
        filename = contract._get_report_base_filename()
        self.assertEqual(filename, f"Contract - {contract.display_name}")
        report = self.env.ref("contract.report_contract")
        self.assertEqual(
            safe_eval(report.print_report_name, {"object": contract, "time": time}),
            filename,
        )
