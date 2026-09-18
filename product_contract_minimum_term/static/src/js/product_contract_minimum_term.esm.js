/* Copyright 2026 Callino - Wolfgang Pichler
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import {ProductContractConfiguratorController} from "@product_contract/js/contract_configurator_controller.esm";
import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {patch} from "@web/core/utils/patch";

const MINIMUM_TERM_FIELDS = [
    "contract_duration_type",
    "min_term_interval",
    "min_term_rule_type",
    "min_term_renewal_interval",
    "min_term_renewal_rule_type",
    "min_term_notice_interval",
    "min_term_notice_rule_type",
];

patch(ProductContractConfiguratorController.prototype, {
    _getProductContractConfiguration(record) {
        const res = super._getProductContractConfiguration(...arguments);
        for (const fname of MINIMUM_TERM_FIELDS) {
            res[fname] = record.data[fname];
        }
        return res;
    },
});

patch(SaleOrderLineProductField.prototype, {
    get contractContext() {
        const res = super.contractContext;
        for (const fname of MINIMUM_TERM_FIELDS) {
            res[`default_${fname}`] = this.props.record.data[fname];
        }
        return res;
    },

    get contractData() {
        const res = super.contractData;
        for (const fname of MINIMUM_TERM_FIELDS) {
            res[fname] = this.props.record.data[fname];
        }
        return res;
    },
});
