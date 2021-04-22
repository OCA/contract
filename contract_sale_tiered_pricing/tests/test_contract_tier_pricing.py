# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import re

from odoo.tests import Form

from .common import TestContractTieredPricing


class TestContractTieredPricingFlow(TestContractTieredPricing):
    def test_cumulated_quantity_history(self):
        self.decimal_price.digits = 6  # without this, there would be rounding issues.
        # However it cannot be put in the setup, because it would get the db precision.
        p = self.decimal_price.precision_get(self.decimal_price.name)  # noqa

        # when
        first_line_qty = 105
        with Form(self.order) as so:
            with so.order_line.new() as line:
                line.product_id = self.product
                line.product_uom_qty = first_line_qty
        first_line = self.order.order_line

        # then
        self.assertEqual(first_line.contract_cumulated_qty, 0)
        self.assertTrue("History = 0" in first_line.name)
        self.assertEqual(first_line.price_subtotal, 10 * 100 + 5 * 8)

        # given
        self.order.action_confirm()
        # let's cheat a bit, but the test would be less interesting without this
        domain_contract_line = [("sale_order_line_id", "=", first_line.id)]
        contract_line = self.env["contract.line"].search(domain_contract_line)
        contract_line.quantity = first_line_qty

        # when
        vals_new_order = {
            "pricelist_id": self.pricelist.id,
            "partner_id": self.partner.id,
        }
        new_order = self.order.create(vals_new_order)
        with Form(new_order) as so:
            with so.order_line.new() as line:
                line.product_id = self.product
                line.product_uom_qty = 100
        second_line = new_order.order_line

        # then
        self.assertEqual(second_line.contract_cumulated_qty, first_line_qty)
        self.assertEqual(second_line.price_subtotal, 95 * 8 + 5 * 7)
        self.assertTrue("History = {}".format(first_line_qty) in second_line.name)
        self.assertEqual(len(re.findall("Tier#1.*PAID", second_line.name)), 1)
        self.assertEqual(len(re.findall("Tier#1", second_line.name)), 1)
        self.assertEqual(len(re.findall("Tier#2.*PAID", second_line.name)), 1)
        self.assertEqual(len(re.findall("Tier#2", second_line.name)), 2)

    def test_translation(self):
        """It's the same test as in sale_tiered_pricing, but it's not redundant.
           Because the description is entirely reimplemented in this module,
           since we need to insert the 'history' information.
           Here we activate the baguette language, and make the customer a baguette.
           Thus when we create a new line, the tier description should be translated
           in baguette.
        """
        Langs = self.env["res.lang"].with_context(active_test=False)
        lang = Langs.search([("code", "=", "fr_FR")])
        lang.active = True
        translations = self.env["ir.translation"]
        translations.load_module_terms(["sale_tiered_pricing"], [lang.code])
        vals_trslt = {
            "name": "addons/contract_sale_tiered_pricing/models/sale_order_line.py",
            "type": "code",
            "module": "sale_tiered_pricing",
            "lang": lang.code,
            "source": "Tier#{}: {:.0f} - {:.2f} - {}",
            "value": "Tranche#{}: {:.0f} - {:.2f} - {}",
            "state": "translated",
        }
        self.env["ir.translation"].create(vals_trslt)
        self.partner.lang = lang.code

        new_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 250,
            }
        )
        self.assertTrue("Tranche" in new_line.name)

    def test_tiered_pricing_discount(self):
        """It's the same test as in sale_tiered_pricing, but it's not redundant.
           Because the logic is partly reimplemented, it could be broken.
        """
        self.product.list_price = 10
        self.tiered_item.tiered_pricelist_id = self.tiered_pricing_discount
        new_line = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product.id,
                "product_uom_qty": 250,
            }
        )
        self.assertEqual(new_line.price_subtotal, 100 * 10 + 100 * 8 + 50 * 5)
        self.assertTrue(" 10" in new_line.name)
        self.assertTrue(" 8" in new_line.name)
        self.assertTrue(" 5" in new_line.name)

    def test_tiered_pricing_base_with_discount(self):
        """We apply a discount on a basic tiered pricing."""
        self.product.list_price = 10
        self.order.pricelist_id = self.pricelist_formula_tier_based_discount
        with Form(self.order) as so:
            with so.order_line.new() as new_line:
                new_line.product_id = self.product
                new_line.product_uom_qty = 250
        # this test would not pass with a new_line = create(...) instead!
        # because we rely on the onchange application logic, a simple
        # get_missing_defaults would not fill the description correctly.
        self.assertEqual(new_line.price_subtotal, 100 * 5 + 100 * 4 + 50 * 3.5)
        self.assertEqual(new_line.discount, 0)
        self.assertTrue(" 5" in new_line.name)
        self.assertTrue(" 4" in new_line.name)
        self.assertTrue(" 3.5" in new_line.name)

    def test_tiered_pricing_base_without_discount(self):
        """Discount not included, so we should get the same price, but a different
           description."""
        self.product.list_price = 10
        self.order.pricelist_id = self.pricelist_formula_tier_based_discount
        self.order.pricelist_id.discount_policy = "without_discount"
        group_discount = self.env.ref("sale.group_discount_per_so_line")
        self.env.user.groups_id = [(4, group_discount.id)]
        with Form(self.order) as so:
            with so.order_line.new() as new_line:
                new_line.product_id = self.product
                new_line.product_uom_qty = 250
        self.assertEqual(new_line.price_subtotal, 100 * 5 + 100 * 4 + 50 * 3.5)
        self.assertEqual(new_line.discount, 50)
        self.assertTrue(" 10" in new_line.name)
        self.assertTrue(" 8" in new_line.name)
        self.assertTrue(" 7" in new_line.name)

    def test_tiered_pricing_base_with_discount_discount(self):
        """We apply a discount on a discount-based tiered pricing."""
        self.product.list_price = 10
        self.tiered_item.tiered_pricelist_id = self.tiered_pricing_discount
        self.order.pricelist_id = self.pricelist_formula_tier_based_discount
        with Form(self.order) as so:
            with so.order_line.new() as new_line:
                new_line.product_id = self.product
                new_line.product_uom_qty = 250
        self.assertEqual(new_line.price_subtotal, 100 * 5 + 100 * 4 + 50 * 2.5)
        self.assertTrue(" 5" in new_line.name)
        self.assertTrue(" 4" in new_line.name)
        self.assertTrue(" 2.5" in new_line.name)
