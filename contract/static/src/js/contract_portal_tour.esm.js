import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("contract_portal_tour", {
    url: "/my",
    steps: () => [
        {
            content: "Go to Contract item",
            trigger: "table.o_portal_my_doc_table tr:first",
            run: "click",
        },
    ],
});
