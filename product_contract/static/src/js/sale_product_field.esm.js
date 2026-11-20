/** @odoo-module **/

import "@sale/js/sale_product_field";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";
import {serializeDate} from "@web/core/l10n/dates";

const SaleOrderLineProductField = registry
    .category("fields")
    .get("sol_product_many2one");

patch(
    SaleOrderLineProductField.prototype,
    "product_contract.SaleOrderLineProductField",
    {
        async _onProductUpdate() {
            await this._super(...arguments);
            if (this.props.record.data.is_contract) {
                this._openContractConfigurator(true);
            }
        },

        _editLineConfiguration() {
            this._super(...arguments);
            if (this.props.record.data.is_contract) {
                this._openContractConfigurator();
            }
        },

        get isConfigurableLine() {
            return this._super(...arguments) || this.props.record.data.is_contract;
        },

        async _openContractConfigurator(isNew = false) {
            const data = this.props.record.data;
            const rootData = this.props.record.model.root.data;
            const actionContext = {
                default_product_id: data.product_id[0],
                default_partner_id: rootData.partner_id[0],
                default_company_id: rootData.company_id[0],
                default_product_uom_qty: data.product_uom_qty,
                default_contract_id: data.contract_id && data.contract_id[0],
                default_recurring_rule_type: data.recurring_rule_type,
                default_recurring_invoicing_type: data.recurring_invoicing_type,
                default_date_start: data.date_start && serializeDate(data.date_start),
                default_date_end: data.date_end && serializeDate(data.date_end),
                default_is_auto_renew: data.is_auto_renew,
                default_auto_renew_interval: data.auto_renew_interval,
                default_auto_renew_rule_type: data.auto_renew_rule_type,
            };
            this.action.doAction(
                "product_contract.product_contract_configurator_action",
                {
                    additionalContext: actionContext,
                    onClose: async (closeInfo) => {
                        if (closeInfo && !closeInfo.special) {
                            this.props.record.update(
                                closeInfo.productContractConfiguration
                            );
                        } else if (isNew) {
                            this.props.record.update({[this.props.name]: undefined});
                        }
                    },
                }
            );
        },
    }
);
