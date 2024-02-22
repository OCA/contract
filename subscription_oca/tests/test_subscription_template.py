from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestSubscriptionTemplate(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.ProductPricelist = cls.env["product.pricelist"]
        cls.SaleSubscription = cls.env["sale.subscription"]
        cls.SubscriptionStage = cls.env["sale.subscription.stage"]
        cls.SubscriptionTemplate = cls.env["sale.subscription.template"]

        cls.draft_stage = cls.env.ref("subscription_oca.subscription_stage_draft")
        cls.in_progress_stage = cls.env.ref(
            "subscription_oca.subscription_stage_in_progress"
        )
        cls.expiring_stage = cls.env.ref("subscription_oca.subscription_stage_expiring")
        cls.closed_stage = cls.env.ref("subscription_oca.subscription_stage_closed")
        cls.all_stages = cls.SubscriptionStage.search([])

        cls.pricelist = cls.ProductPricelist.create(
            {
                "name": "Test Pricelist",
                "currency_id": cls.env.ref("base.USD").id,
            }
        )
        cls.template = cls.SubscriptionTemplate.create(
            {
                "name": "Test Template",
            }
        )

    def test_stage_validity(self):
        with self.assertRaises(ValidationError):
            self.SubscriptionTemplate.create(
                {
                    "name": "Test Template",
                    "recurring_rule_boundary": "unlimited",
                    "stage_ids": [(6, 0, self.all_stages.ids)],
                }
            )

    def test_expiring_validities(self):
        with self.assertRaises(ValidationError):
            self.template.write({"stage_ids": [(4, self.expiring_stage.id)]})
        self.template.write(
            {
                "recurring_rule_boundary": "limited",
                "recurring_rule_type": "months",
                "recurring_interval": 3,
                "stage_ids": [(4, self.expiring_stage.id)],
            }
        )
        new_expiring_stage = self.SubscriptionStage.create(
            {
                "name": "New Expiring Stage",
                "type": "expiring",
            }
        )
        with self.assertRaises(ValidationError):
            self.template.write({"stage_ids": [(4, new_expiring_stage.id)]})

    def test_has_expiring(self):
        self.template.write(
            {
                "recurring_rule_boundary": "limited",
                "recurring_rule_type": "months",
                "recurring_interval": 3,
            }
        )
        self.assertFalse(self.template.has_expiring)
        expiring_stage = self.env.ref("subscription_oca.subscription_stage_expiring")
        self.template.write({"stage_ids": [(4, expiring_stage.id)]})
        self.template._onchange_stage_ids()
        self.assertTrue(self.template.has_expiring)

    def test_cron_expired(self):
        self.template.write(
            {
                "recurring_rule_boundary": "limited",
                "recurring_rule_type": "months",
                "recurring_interval": 3,
                "stage_ids": [(4, self.expiring_stage.id)],
                "days_before_expiring": 42,
            }
        )
        sub = self.SaleSubscription.create(
            {
                "partner_id": self.env.ref("base.res_partner_address_28").id,
                "template_id": self.template.id,
                "pricelist_id": self.pricelist.id,
                "date_start": fields.Date.today() - relativedelta(months=3),
            }
        )
        sub.stage_id = self.in_progress_stage.id
        self.SubscriptionTemplate.cron_expiring_subscriptions()
        self.assertEqual(sub.stage_id, self.expiring_stage)
