# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models
from odoo.exceptions import UserError


class SaleSubscriptionChangePartnerWizard(models.TransientModel):
    _name = "sale.subscription.change.partner.wizard"
    _description = "Change customer wizard for subscriptions"

    subscription_ids = fields.Many2many(
        comodel_name="sale.subscription",
        string="Subscriptions",
        default=lambda self: self._default_subscription_ids(),
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        string="New customer",
    )
    update_pricelist = fields.Boolean(
        string="Apply customer pricelist",
        default=True,
    )
    update_fiscal_position = fields.Boolean(
        string="Recompute fiscal position",
        default=True,
    )

    def _default_subscription_ids(self):
        active_ids = self.env.context.get("active_ids")
        if not active_ids:
            return self.env["sale.subscription"]
        return self.env["sale.subscription"].browse(active_ids)

    def _prepare_subscription_values(self, subscription):
        """Build the values to write on a single subscription. The new
        customer drives the partner and, optionally, the sale pricelist and the
        fiscal position, all in a single write."""
        values = {"partner_id": self.partner_id.id}
        if self.update_pricelist:
            pricelist = self.partner_id.with_company(
                subscription.company_id
            ).property_product_pricelist
            if pricelist:
                values["pricelist_id"] = pricelist.id
        if self.update_fiscal_position:
            values["fiscal_position_id"] = (
                subscription._get_fiscal_position_from_partner(self.partner_id).id
            )
        return values

    def action_apply(self):
        self.ensure_one()
        if not self.subscription_ids:
            raise UserError(
                self.env._("No subscriptions selected to change customer on.")
            )
        for subscription in self.subscription_ids:
            if subscription.stage_id.type == "post":
                raise UserError(
                    self.env._(
                        "Cannot change the customer of a closed subscription "
                        "(%(name)s).",
                        name=subscription.display_name,
                    )
                )
            old_partner = subscription.partner_id
            if old_partner == self.partner_id:
                # Nothing to change: skip to avoid noisy chatter and writes.
                continue
            subscription.write(self._prepare_subscription_values(subscription))
            subscription.message_post(
                body=self.env._(
                    "Customer changed from %(old)s to %(new)s.",
                    old=old_partner.display_name,
                    new=self.partner_id.display_name,
                )
            )
        return {"type": "ir.actions.act_window_close"}
