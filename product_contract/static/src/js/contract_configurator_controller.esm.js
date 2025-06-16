import {formView} from "@web/views/form/form_view";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class ProductContractConfiguratorController extends formView.Controller {
    setup() {
        super.setup();
        this.action = useService("action");
    }

    _getProductContractConfiguration(record) {
        const {
            product_uom_qty,
            recurrence_number,
            recurring_interval,
            recurring_rule_type,
            recurrence_interval,
            contract_id,
            date_start,
            date_end,
            contract_line_id,
            is_auto_renew,
            auto_renew_interval,
            auto_renew_rule_type,
        } = record.data;
        return {
            product_uom_qty,
            recurrence_number,
            recurring_interval,
            recurring_rule_type,
            recurrence_interval,
            contract_id,
            date_start,
            date_end,
            contract_line_id,
            is_auto_renew,
            auto_renew_interval,
            auto_renew_rule_type,
        };
    }

    async onRecordSaved(record) {
        await super.onRecordSaved(...arguments);
        return this.action.doAction({
            type: "ir.actions.act_window_close",
            infos: {
                productContractConfiguration:
                    this._getProductContractConfiguration(record),
            },
        });
    }
}

registry.category("views").add("product_contract_configurator_form", {
    ...formView,
    Controller: ProductContractConfiguratorController,
});
