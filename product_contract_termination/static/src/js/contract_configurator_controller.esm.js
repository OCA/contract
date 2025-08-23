import {ProductContractConfiguratorController} from "@product_contract/static/src/js/contract_configurator_controller";
import {patch} from "@web/core/utils/patch";

patch(ProductContractConfiguratorController.prototype, {
    /**
     * @override
     */
     _getProductContractConfiguration(record) {
        const {
            product_uom_qty,
            recurrence_number,
            recurring_interval,
            recurring_rule_type,
            recurrence_interval,
            recurring_invoicing_type,
            contract_id,
            date_start,
            date_end,
            contract_line_id,
            is_auto_renew,
            termination_notice_interval,
            termination_notice_rule_type,
            automatic_price,
            auto_renew_interval,
            manual_renew_needed,
            auto_renew_rule_type,
            contract_start_date_method,
        } = record.data;
        return {
            product_uom_qty,
            recurrence_number,
            recurring_interval,
            recurring_rule_type,
            recurrence_interval,
            recurring_invoicing_type,
            contract_id,
            date_start,
            date_end,
            contract_line_id,
            is_auto_renew,
            termination_notice_interval,
            termination_notice_rule_type,
            automatic_price,
            auto_renew_interval,
            manual_renew_needed,
            auto_renew_rule_type,
            contract_start_date_method,
        };
    },
});


