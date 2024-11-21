/** @odoo-module **/

import {patch} from "@web/core/utils/patch";
import {SaleOrderLineProductField} from "@sale/js/sale_product_field";

patch(SaleOrderLineProductField.prototype, {
    _getContractConfiguratorContext() {
        const context = super._getContractConfiguratorContext();
        if (this.props.record.data.qty_type) {
            context.default_qty_type = this.props.record.data.qty_type;
        }
        if (this.props.record.data.qty_formula_id) {
            context.default_qty_formula_id = this.props.record.data.qty_formula_id[0];
        }
        return context;
    },
});
