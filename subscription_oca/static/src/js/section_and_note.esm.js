/* Copyright 2026 Domatix
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {
    SectionAndNoteFieldOne2Many,
    SectionAndNoteListRenderer,
    sectionAndNoteFieldOne2Many,
} from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";
import {registry} from "@web/core/registry";

export class SubscriptionSectionListRenderer extends SectionAndNoteListRenderer {
    setup() {
        super.setup();
        this.copyFields.push("invoice_once");
    }

    async toggleInvoiceOnce(record) {
        await record.update({invoice_once: !record.data.invoice_once});
    }
}

export class SubscriptionSectionOne2Many extends SectionAndNoteFieldOne2Many {
    static components = {
        ...SectionAndNoteFieldOne2Many.components,
        ListRenderer: SubscriptionSectionListRenderer,
    };
}

export const subscriptionSectionOne2Many = {
    ...sectionAndNoteFieldOne2Many,
    component: SubscriptionSectionOne2Many,
};

registry
    .category("fields")
    .add("subscription_oca_section_and_note_one2many", subscriptionSectionOne2Many);
