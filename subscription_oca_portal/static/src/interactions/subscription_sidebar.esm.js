/* Copyright 2026 Domatix
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {Sidebar} from "@portal/interactions/sidebar";
import {registry} from "@web/core/registry";

export class SubscriptionSidebar extends Sidebar {
    static selector = ".o_portal_subscription_sidebar";

    setup() {
        super.setup();
        this.spyWatched = document.querySelector("body[data-target='.navspy']");
    }

    start() {
        super.start();
        // Build the sidebar navigation from the document headers.
        this.generateMenu();
    }
}

registry
    .category("public.interactions")
    .add("subscription_oca_portal.subscription_sidebar", SubscriptionSidebar);
