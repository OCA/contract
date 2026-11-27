# Copyright 2026 Open User Systems - Chris Mann
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleSubscriptionTemplate(models.Model):
    _inherit = "sale.subscription.template"

    auto_create_payment = fields.Boolean(
        string="Automatic payment",
        help="Charge the subscription's payment token when invoicing. "
        "The invoice is posted once the payment succeeds.",
    )
    payment_failure_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Payment Failure Email",
        domain="[('model', '=', 'account.move')]",
        help="Sent to the customer when an automatic payment fails. Leave "
        "empty if the payment provider already notifies the customer.",
    )
    auto_retry_payment = fields.Boolean(
        string="Retry failed payments",
        help="Automatically charge a failed payment again. Leave unticked if "
        "the payment provider retries failed payments itself, to avoid "
        "charging the customer twice.",
    )
    auto_retry_payment_count = fields.Integer(
        string="Payment retries",
        default=3,
        help="Number of times a failed payment is charged again.",
    )
    auto_retry_payment_hours = fields.Integer(
        string="Hours between retries",
        default=24,
    )
