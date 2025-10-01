import {registry} from "@web/core/registry";

registry.category("web_tour.tours").add("contract_portal_tour", {
    url: "/",
    steps: () => [
        {
            content: "Go to Contracts menu",
            trigger: 'a[href*="/my/contracts"]',
            run: "click",
            expectUnloadPage: true,
        },
        {
            content: "Go to Contract item",
            trigger: "table.o_portal_my_doc_table tr:first",
            run: "click",
        },
    ],
});
