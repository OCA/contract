from odoo.exceptions import ValidationError
from odoo.tests.common import SavepointCase


class TestSubscriptionStage(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_single_default_create(self):
        with self.assertRaises(ValidationError):
            self.env["sale.subscription.stage"].create(
                {
                    "name": "New Default 'In Progress' Stage",
                    "type": "in_progress",
                    "is_default": True,
                }
            )

    def test_single_default_edit(self):
        new_stage = self.env["sale.subscription.stage"].create(
            {
                "name": "New Default 'In Progress' Stage",
                "type": "in_progress",
            }
        )
        with self.assertRaises(ValidationError):
            new_stage.is_default = True
