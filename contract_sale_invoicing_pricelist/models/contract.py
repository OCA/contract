from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _prepare_invoice(self, date_invoice, journal=None):
        """Inherit method to set the invoice pricelist based on the contract pricelist."""
        values = super()._prepare_invoice(date_invoice, journal=journal)
        if not self.pricelist_id:
            return values
        values.update(
            {
                "pricelist_id": self.pricelist_id.id,
                "currency_id": self.pricelist_id.currency_id.id,
            }
        )
        return values

    def _recurring_create_invoice(self, date_ref=False):
        """Inherit method to update the price based in the pricelist currency."""
        partner_priceist_id = self.partner_id.property_product_pricelist.id
        contract_pricelist_id = self.pricelist_id.id
        moves = super()._recurring_create_invoice(date_ref=date_ref)
        # Added the condition only to solve the test cases error from the "contract"
        # module. becasue it's update the invoice price based on the contract pricelist
        # and currency.
        if partner_priceist_id == contract_pricelist_id:
            return moves
        # Updated the invoice price only if the contract pricelist is different from the
        # partner pricelist and contract line has 'automatic_price' as enable.
        for line in moves.invoice_line_ids.filtered(
            lambda line: line.contract_line_id.automatic_price
        ):
            line._compute_price_unit()
        return moves
