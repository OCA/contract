# Copyright 2020 Tecnativa - Víctor Martínez
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

import json

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
