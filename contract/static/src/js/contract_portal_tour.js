odoo.define("contract.tour", function (require) {
    "use strict";

    var tour = require("web_tour.tour");

    tour.register(
        "contract_portal_tour",
        {
            test: true,
            url: "/my",
        },
        [
            {
                content: "Go /my/contracts url",
                trigger: 'a[href*="/my/contracts"]',
            },
            {
                content: "Go to Contract item",
                trigger: ".tr_contract_link:eq(0)",
            },
        ]
    );
});
