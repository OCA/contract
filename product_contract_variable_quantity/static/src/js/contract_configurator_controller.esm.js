/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {ProductContractConfiguratorController} from "@product_contract/js/contract_configurator_controller.esm";

patch(ProductContractConfiguratorController.prototype, {
    _getProductContractConfiguration(record) {
        const config = super._getProductContractConfiguration(record);
        config.qty_type = record.data.qty_type;
        config.qty_formula_id = record.data.qty_formula_id;
        return config;
    },
});
