# SPDX-FileCopyrightText: 2025 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def _prepare_sale(self, date_ref):
        sale_values = super()._prepare_sale(date_ref)
        sale_values["payment_mode_id"] = self.payment_mode_id.id
        return sale_values
