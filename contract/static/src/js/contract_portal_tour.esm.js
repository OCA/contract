import {redirect} from "@web/core/utils/urls";
import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("contract_portal_tour", {
    url: "/my",
    wait_for: Promise.resolve(odoo.__TipTemplateDef),
    steps: () => [
        {
            content: "Go /my/contracts url",
            trigger: 'a[href*="/my/contracts"]',
            run: function () {
                redirect("/my/contracts");
            },
        },
        {
            content: "Go to Contract item",
            trigger: "table.o_portal_my_doc_table tr:eq(0)",
        },
    ],
});
