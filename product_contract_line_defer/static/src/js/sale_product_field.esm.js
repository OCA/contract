// Copyright 2025 ACSONE SA/NV (<http://acsone.eu>)
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import {SaleOrderLineProductField} from "@sale/js/sale_product_field";
import {patch} from "@web/core/utils/patch";

patch(SaleOrderLineProductField.prototype, {
    get contractContext() {
        const context = super.contractContext;
        if (this.props.record.data.is_deferred) {
            context.default_is_deferred = this.props.record.data.is_deferred;
        }
        return context;
    },
});
