/** @odoo-module **/

import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {Record, RelationalModel} from "@web/views/relational_model";

export class ProductContractConfiguratorRelationalModel extends RelationalModel {}

export class ProductContractConfiguratorRecord extends Record {
    /**
     * Let the regular save run (validates required fields), then close the
     * dialog handing the configuration back to the caller.
     *
     * @override
     */
    async save() {
        const isSaved = await super.save(...arguments);
        if (!isSaved) {
            return false;
        }
        const data = this.data;
        this.model.action.doAction({
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
        return true;
    }
}

ProductContractConfiguratorRelationalModel.Record = ProductContractConfiguratorRecord;

registry.category("views").add("product_contract_configurator_form", {
    ...formView,
    Model: ProductContractConfiguratorRelationalModel,
});
