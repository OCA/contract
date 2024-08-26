/** @odoo-module **/

import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ProductContractConfiguratorController extends formView.Controller {
    setup() {
        super.setup();
        this.action = useService("action");
    }

    async onRecordSaved(record) {
        await super.onRecordSaved(...arguments);
        const {
            product_uom_qty,
            contract_id,
            recurring_rule_type,
            recurring_invoicing_type,
            date_start,
            date_end,
            contract_line_id,
            is_auto_renew,
            auto_renew_interval,
            auto_renew_rule_type,
        } = record.data;
        return this.action.doAction({
            type: "ir.actions.act_window_close",
            infos: {
                productContractConfiguration: {
                    product_uom_qty,
                    contract_id,
                    recurring_rule_type,
                    recurring_invoicing_type,
                    date_start,
                    date_end,
                    contract_line_id,
                    is_auto_renew,
                    auto_renew_interval,
                    auto_renew_rule_type,
                },
            },
        });
    }
}

registry.category("views").add("product_contract_configurator_form", {
    ...formView,
    Controller: ProductContractConfiguratorController,
});
