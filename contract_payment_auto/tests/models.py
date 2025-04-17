from odoo import models


class TransactionTest(models.Model):
    _inherit = "payment.transaction"

    def _send_payment_request(self):
        tr_state = self.env.context["test_target_state"]
        if tr_state == "Exception":
            raise Exception("error in _send_payment_request")
        self.state = tr_state
