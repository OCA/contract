# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons import decimal_precision as dp


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    contract_cumulated_qty = fields.Float(
        string="Contract Cumulated Quantity",
        help="This takes into account all products with a running contract line",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_contract_cumulated_qty",
        required=True,
        default=0,
        store=True,
        copy=False,
    )

    def _get_running_lines(self, one=False):
        self.ensure_one()
        partner_id = self.order_id.partner_id.commercial_partner_id.id
        domain_lines = [
            ("product_id", "=", self.product_id.id),
            ("contract_id.partner_id", "child_of", partner_id),
            ("date_start", "<=", self.date_start),
            ("date_end", ">=", self.date_end),
            ("is_canceled", "=", False),
        ]
        return self.env["contract.line"].search(domain_lines, limit=1 if one else None)

    def recompute_price_and_description(self):
        for line in self:
            product = line._get_contextualized_product()
            product.invalidate_cache(fnames=["price"], ids=product.ids)
            line.price_unit = line._get_display_price(product)
            line.name = line.get_sale_order_line_multiline_description_sale(product)

    @api.onchange("date_start")
    def onchange_date_start(self):
        if self.product_id:
            self.recompute_price_and_description()

    @api.depends(
        "product_uom",
        "product_id",
        "order_id.partner_id.commercial_partner_id",
        "date_start",
        "date_end",
    )
    def _compute_contract_cumulated_qty(self):
        dated = self.filtered(lambda cl: cl.date_start and cl.date_end)
        contracts = dated.filtered("product_id.is_contract")
        for line in contracts:
            if line.product_uom != line.product_id.uom_id:
                line.product_uom = line.product_id.uom_id
            uom = line.product_uom
            running_lines = line._get_running_lines()
            if uom:
                get_qty = lambda l: l.uom_id._compute_quantity(l.quantity, uom)  # noqa
                qty = sum(running_lines.mapped(get_qty))
            else:
                qty = sum(running_lines.mapped("quantity"))
            line.contract_cumulated_qty = qty
        for line in self - contracts:
            line.contract_cumulated_qty = 0

    def get_sale_order_line_multiline_description_sale(self, product):
        """Enrich the description with the tier computation.
        """
        skip_tier_description = self.env.context.get("skip_tier_description")
        if self.is_tier_priced and self.product_uom_qty and not skip_tier_description:
            context = {"lang": self.order_id.partner_id.lang}
            res = super(
                SaleOrderLine, self.with_context(skip_tier_description=True)
            ).get_sale_order_line_multiline_description_sale(product)
            qty, cumulated_qty = self.product_uom_qty, self.contract_cumulated_qty
            self._get_display_price(product)
            qps = product.tiered_qps
            self_trnslt = self.with_context(**context)
            desc = self_trnslt._get_tiered_pricing_description(qty, cumulated_qty, qps)
            res = "\n".join([res, desc])
        else:
            res = super(
                SaleOrderLine, self
            ).get_sale_order_line_multiline_description_sale(product)
        return res

    def _get_tiered_pricing_description(self, qty, cumulated_qty, qps):
        pricelist = self.order_id.pricelist_id
        line = self._get_running_lines(one=True)
        if cumulated_qty:
            contract_end = line.date_end
            msg_tmp = _(
                "History = {:.0f} (main contract running until {}), "
                "new order of {:.0f} units from {} to {} on pricelist {}."
            )
            start, end = self.date_start, self.date_end
            params = [cumulated_qty, contract_end, qty, start, end, pricelist.name]
            msg_history = msg_tmp.format(*params)
        else:
            msg_tmp = _("History = {:.0f}, order of {:.0f} units on pricelist {}.")
            msg_history = msg_tmp.format(cumulated_qty, qty, pricelist.name)
        msg_pl = _(
            "Your pricelist is based on the principle of tiered pricing to help you "
            "benefit from discounts on volume. The unit price, the total price "
            "on your order are calculated as follows:"
            "\nTier - Quantity in tier - Tier price - Value of tier"
        )
        msg_tiers = self._get_tier_description(qty, cumulated_qty, qps)
        return "\n".join([msg_history, msg_pl] + msg_tiers)

    def _get_tier_description(self, qty, cumulated_qty, qps):
        if (
            self.price_unit
            and sum(q * p for q, p in qps)
            and self.order_id.pricelist_id.discount_policy == "with_discount"
        ):
            ratio = self.price_unit / sum(q * p for q, p in qps) * self.product_uom_qty
            qps = [(q, p * round(ratio, 3)) for q, p in qps]
        msg_tiers = []
        msg_tier = _("Tier#{}: {:.0f} - {:.2f} - {}")
        paid = _("PAID")
        for i in range(len(qps)):
            q, p = qps[i]
            already_paid = cumulated_qty >= q
            if already_paid:
                cumulated_qty = cumulated_qty - q
            elif cumulated_qty > 0:
                msg_tiers.append(msg_tier.format(i + 1, cumulated_qty, p, paid))
                q -= cumulated_qty
                cumulated_qty = 0
            value = paid if already_paid else "{:.2f}".format(q * p)
            msg_tiers.append(msg_tier.format(i + 1, q, p, value))
            qty -= q
        return msg_tiers

    def _get_display_price(self, product):
        if self.is_tier_priced and self.product_uom_qty and self.contract_cumulated_qty:
            ccq = self.contract_cumulated_qty
            qty = self.product_uom_qty
            product_ccq = product.with_context(quantity=ccq)
            ccq_price = super(SaleOrderLine, self)._get_display_price(product_ccq)
            product.invalidate_cache(fnames=["price"], ids=product.ids)
            product_total = product.with_context(quantity=ccq + qty)
            product.tiered_qps = product_total.tiered_qps
            total_price = super(SaleOrderLine, self)._get_display_price(product_total)
            price = ((total_price * (ccq + qty)) - (ccq * ccq_price)) / qty
        else:
            price = super(SaleOrderLine, self)._get_display_price(product)
        return price
