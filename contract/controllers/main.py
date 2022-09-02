# Copyright 2020-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class PortalContract(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "contract_count" in counters:
            contract_model = request.env["contract.contract"]
            contract_count = (
                contract_model.search_count([])
                if contract_model.check_access_rights("read", raise_exception=False)
                else 0
            )
            values["contract_count"] = contract_count
        return values

    def _contract_get_page_view_values(self, contract, access_token, **kwargs):
        values = {
            "page_name": "Contracts",
            "contract": contract,
        }
        return self._get_page_view_values(
            contract, access_token, values, "my_contracts_history", False, **kwargs
        )

    def _get_filter_domain(self, kw):
        return []

    @http.route(
        ["/my/contracts", "/my/contracts/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_contracts(
        self, page=1, date_begin=None, date_end=None, sortby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        contract_obj = request.env["contract.contract"]
        # Avoid error if the user does not have access.
        if not contract_obj.check_access_rights("read", raise_exception=False):
            return request.redirect("/my")
        domain = self._get_filter_domain(kw)
        searchbar_sortings = {
            "date": {"label": _("Date"), "order": "recurring_next_date desc"},
            "name": {"label": _("Name"), "order": "name desc"},
            "code": {"label": _("Reference"), "order": "code desc"},
        }
        # default sort by order
        if not sortby:
            sortby = "date"
        order = searchbar_sortings[sortby]["order"]
        # count for pager
        contract_count = contract_obj.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/contracts",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
            },
            total=contract_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        contracts = contract_obj.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_contracts_history"] = contracts.ids[:100]
        values.update(
            {
                "date": date_begin,
                "contracts": contracts,
                "page_name": "Contracts",
                "pager": pager,
                "default_url": "/my/contracts",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("contract.portal_my_contracts", values)

    @http.route(
        ["/my/contracts/<int:contract_contract_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_contract_detail(self, contract_contract_id, access_token=None, **kw):
        try:
            contract_sudo = self._document_check_access(
                "contract.contract", contract_contract_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")
        values = self._contract_get_page_view_values(contract_sudo, access_token, **kw)
        return request.render("contract.portal_contract_page", values)
