// Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import {ProductContractConfiguratorController} from "@product_contract/js/contract_configurator_controller.esm";
import {patch} from "@web/core/utils/patch";

patch(ProductContractConfiguratorController.prototype, {
    _getProductContractConfiguration(record) {
        const config = super._getProductContractConfiguration(record);
        config.is_deferred = record.data.is_deferred;
        return config;
    },
});
