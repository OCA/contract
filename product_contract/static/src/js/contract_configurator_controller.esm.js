/** @odoo-module **/

import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ProductContractConfiguratorController extends formView.Controller {
    setup() {
        super.setup();
        this.action = useService("action");
    }

    async save() {
        const saved = await super.save(...arguments);
        if (!saved) {
            return saved;
        }
        const data = this.model.root.data;
        await this.action.doAction({
            type: "ir.actions.act_window_close",
            infos: {
                productContractConfiguration: {
                    product_uom_qty: data.product_uom_qty,
                    contract_id: data.contract_id,
                    recurring_rule_type: data.recurring_rule_type,
                    recurring_invoicing_type: data.recurring_invoicing_type,
                    date_start: data.date_start,
                    date_end: data.date_end,
                    contract_line_id: data.contract_line_id,
                    is_auto_renew: data.is_auto_renew,
                    auto_renew_interval: data.auto_renew_interval,
                    auto_renew_rule_type: data.auto_renew_rule_type,
                },
            },
        });
        return saved;
    }
}

registry.category("views").add("product_contract_configurator_form", {
    ...formView,
    Controller: ProductContractConfiguratorController,
});
