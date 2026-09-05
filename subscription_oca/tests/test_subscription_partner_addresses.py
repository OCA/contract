# Copyright 2026 Domatix - Alvaro
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestSubscriptionPartnerAddresses(AccountTestInvoicingCommon):
    """Invoice and delivery addresses configured on the subscription must be
    propagated to the recurring invoices and to the generated sale orders."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.env.user.group_ids += cls.env.ref("sales_team.group_sale_manager")
        cls.addr_customer = cls.env["res.partner"].create({"name": "Main customer"})
        cls.addr_invoice_address = cls.env["res.partner"].create(
            {
                "name": "Billing dept",
                "type": "invoice",
                "parent_id": cls.addr_customer.id,
            }
        )
        cls.addr_shipping_address = cls.env["res.partner"].create(
            {
                "name": "Warehouse",
                "type": "delivery",
                "parent_id": cls.addr_customer.id,
            }
        )
        # Prefixed on purpose: AccountTestInvoicingCommon < ProductCommon already
        # defines cls.pricelist (and cls.company/cls.product_a); avoid shadowing.
        cls.addr_pricelist = cls.env["product.pricelist"].create(
            {"name": "Addr PL", "currency_id": cls.company.currency_id.id}
        )
        cls.addr_template = cls.env["sale.subscription.template"].create(
            {
                "name": "Addr template",
                "code": "ADDR",
                "recurring_rule_type": "months",
                "recurring_interval": 1,
                "invoice_state": "draft",
            }
        )
        cls.addr_stage = cls.env["sale.subscription.stage"].search(
            [("type", "=", "in_progress")], limit=1
        )

    def _new_subscription(self, partner):
        sub = self.env["sale.subscription"].create(
            {
                "partner_id": partner.id,
                "template_id": self.addr_template.id,
                "pricelist_id": self.addr_pricelist.id,
                "stage_id": self.addr_stage.id,
            }
        )
        self.env["sale.subscription.line"].create(
            {
                "sale_subscription_id": sub.id,
                "product_id": self.product_a.id,
                "product_uom_qty": 1.0,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [])],
            }
        )
        return sub

    def test_addresses_default_from_partner_children(self):
        sub = self._new_subscription(self.addr_customer)
        self.assertEqual(sub.partner_invoice_id, self.addr_invoice_address)
        self.assertEqual(sub.partner_shipping_id, self.addr_shipping_address)

    def test_addresses_default_to_partner_without_children(self):
        plain = self.env["res.partner"].create({"name": "No child"})
        sub = self._new_subscription(plain)
        self.assertEqual(sub.partner_invoice_id, plain)
        self.assertEqual(sub.partner_shipping_id, plain)

    def test_addresses_empty_without_partner(self):
        # A record without partner yet (e.g. while filling the form) must
        # keep both addresses empty instead of crashing.
        sub = self.env["sale.subscription"].new({})
        self.assertFalse(sub.partner_invoice_id)
        self.assertFalse(sub.partner_shipping_id)

    def test_invoice_uses_subscription_addresses(self):
        sub = self._new_subscription(self.addr_customer)
        invoice = sub.create_invoice()
        # The invoice is addressed to the invoice address, with its delivery one.
        self.assertEqual(invoice.partner_id, self.addr_invoice_address)
        self.assertEqual(invoice.partner_shipping_id, self.addr_shipping_address)

    def test_invoice_commercial_partner_rolls_up_to_customer(self):
        # Addressing the invoice to a child invoice contact must not move the
        # receivable away from the contracting company.
        sub = self._new_subscription(self.addr_customer)
        invoice = sub.create_invoice()
        self.assertEqual(invoice.commercial_partner_id, self.addr_customer)

    def test_invoice_follows_manual_address_override(self):
        other_invoice = self.env["res.partner"].create(
            {
                "name": "Alt billing",
                "type": "invoice",
                "parent_id": self.addr_customer.id,
            }
        )
        sub = self._new_subscription(self.addr_customer)
        sub.partner_invoice_id = other_invoice
        invoice = sub.create_invoice()
        self.assertEqual(invoice.partner_id, other_invoice)

    def test_sale_order_carries_addresses(self):
        self.addr_template.create_sale_order = True
        self.addr_template.invoice_state = "posted"
        sub = self._new_subscription(self.addr_customer)
        order = sub.create_sale_order()
        self.assertEqual(order.partner_id, self.addr_customer)
        self.assertEqual(order.partner_invoice_id, self.addr_invoice_address)
        self.assertEqual(order.partner_shipping_id, self.addr_shipping_address)
