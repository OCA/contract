/** @odoo-module **/

import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("contract_portal_tour", {
    test: true,
    url: "/my",
    steps: () => [
        {
            content: "Go /my/contracts url",
            trigger: 'a[href*="/my/contracts"]',
        },
        {
            content: "Go to Contract item",
            trigger: ".tr_contract_link:eq(0)",
        },
    ],
});
