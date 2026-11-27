# Copyright 2020 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import json

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

    def test_portal_contract_type_split(self):
        partner = self.env["res.partner"].create({"name": "partner both sides"})
        customer, supplier = self.env["contract.contract"].create(
            [
                {
                    "name": "Customer Contract",
                    "partner_id": partner.id,
                    "contract_type": "sale",
                },
                {
                    "name": "Supplier Contract",
                    "partner_id": partner.id,
                    "contract_type": "purchase",
                },
            ]
        )
        (customer | supplier).message_subscribe(partner_ids=partner.ids)
        self._create_new_portal_user(
            partner_id=partner.id, login="portal_split", password="portal_split"
        )
        self.authenticate("portal_split", "portal_split")
        http.root.session_store.save(self.session)

        counters = self.url_open(
            url="/my/counters",
            data=json.dumps(
                {"params": {"counters": ["contract_count", "supplier_contract_count"]}}
            ),
            headers={"Content-Type": "application/json"},
        ).json()["result"]
        self.assertEqual(counters["contract_count"], 1)
        self.assertEqual(counters["supplier_contract_count"], 1)
        home = self.url_open(url="/my").text
        self.assertIn("Your Contracts", home)
        self.assertIn("Our Contracts", home)

        customer_page = self.url_open(url="/my/contracts?filterby=customer").text
        self.assertIn(customer.name, customer_page)
        self.assertNotIn(supplier.name, customer_page)
        supplier_page = self.url_open(url="/my/contracts?filterby=supplier").text
        self.assertIn(supplier.name, supplier_page)
        self.assertNotIn(customer.name, supplier_page)

    def test_portal_contract_empty_list(self):
        partner = self.env["res.partner"].create({"name": "partner no contracts"})
        self._create_new_portal_user(
            partner_id=partner.id, login="portal_empty", password="portal_empty"
        )
        self.authenticate("portal_empty", "portal_empty")
        http.root.session_store.save(self.session)
        page = self.url_open(url="/my/contracts").text
        self.assertIn("alert-warning", page)
        self.assertNotIn("o_portal_my_doc_table", page)

    def test_portal_contract_report(self):
        """The sidebar "View Details" button renders the contract report."""
        partner = self.env["res.partner"].create({"name": "partner test report"})
        contract = self.env["contract.contract"].create(
            {"name": "Reported Contract", "partner_id": partner.id}
        )
        self._create_new_portal_user(
            partner_id=partner.id, login="portal_report", password="portal_report"
        )
        url_report = (
            f"/my/contracts/{contract.id}"
            f"?access_token={contract._portal_ensure_token()}&report_type=html"
        )
        # Anonymous visitor coming from the e-mail link: the token alone grants
        # access.
        response = self.url_open(url=url_report)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recurring Items", response.text)
        # Logged-in portal user
        self.authenticate("portal_report", "portal_report")
        http.root.session_store.save(self.session)
        response = self.url_open(url=url_report)
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
