/* Copyright 2026 Domatix
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {
    contains,
    defineModels,
    fields,
    models,
    mountView,
} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {animationFrame} from "@odoo/hoot-dom";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class SubscriptionLine extends models.Model {
    _name = "subscription_line";
    _records = [
        {
            id: 1,
            name: "One-time",
            display_type: "line_section",
            sequence: 1,
            invoice_once: true,
        },
        {
            id: 2,
            name: "Setup",
            display_type: false,
            sequence: 2,
            invoice_once: false,
        },
        {
            id: 3,
            name: "Monthly",
            display_type: "line_section",
            sequence: 3,
            invoice_once: false,
        },
        {
            id: 4,
            name: "Support",
            display_type: false,
            sequence: 4,
            invoice_once: false,
        },
    ];

    name = fields.Char();
    display_type = fields.Selection({
        selection: [
            ["line_section", "Section"],
            ["line_note", "Note"],
        ],
    });
    sequence = fields.Integer();
    invoice_once = fields.Boolean();
}

class Subscription extends models.Model {
    _name = "subscription";
    _records = [{id: 1, line_ids: [1, 2, 3, 4]}];

    line_ids = fields.One2many({relation: "subscription_line"});
}

defineModels([Subscription, SubscriptionLine]);
defineMailModels();

const ARCH = `
    <form>
        <field name="line_ids" widget="subscription_oca_section_and_note_one2many">
            <list editable="bottom">
                <field name="sequence" widget="handle"/>
                <field name="display_type" column_invisible="1"/>
                <field name="invoice_once" column_invisible="1"/>
                <field name="name" widget="section_and_note_text"/>
            </list>
        </field>
    </form>
`;

test("shows the invoice once option in the section menu", async () => {
    await mountView({
        type: "form",
        resModel: "subscription",
        resId: 1,
        arch: ARCH,
    });

    await contains(".o_list_section_options:eq(0) button").click();
    expect(".o-dropdown-item:contains(Invoice once)").toHaveCount(1);
    expect(".o-dropdown-item:contains(Invoice once) i").toHaveClass(
        "fa-check-square-o"
    );

    await contains(".o_list_section_options:eq(1) button").click();
    expect(".o-dropdown-item:contains(Invoice once) i").toHaveClass("fa-square-o");
});

test("toggles invoice once from the section menu", async () => {
    await mountView({
        type: "form",
        resModel: "subscription",
        resId: 1,
        arch: ARCH,
    });

    await contains(".o_list_section_options:eq(1) button").click();
    await contains(".o-dropdown-item:contains(Invoice once)").click();
    await animationFrame();

    await contains(".o_list_section_options:eq(1) button").click();
    expect(".o-dropdown-item:contains(Invoice once) i").toHaveClass(
        "fa-check-square-o"
    );
});

test("duplicates the invoice once flag with the section", async () => {
    await mountView({
        type: "form",
        resModel: "subscription",
        resId: 1,
        arch: ARCH,
    });

    await contains(".o_list_section_options:eq(0) button").click();
    await contains(".o-dropdown-item:contains(Duplicate)").click();
    await animationFrame();

    await contains(".o_list_section_options:eq(1) button").click();
    expect(".o-dropdown-item:contains(Invoice once) i").toHaveClass(
        "fa-check-square-o"
    );
});
