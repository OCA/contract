# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AutoInvoiceSuspensionReason(models.Model):
    _name = "contract.automatic.invoice.suspension.reason"
    _description = "contract automatic invoice suspension reason"
    _order = "sequence"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    parent_id = fields.Many2one(
        comodel_name="contract.automatic.invoice.suspension.reason",
        string="Parent Auto Invoice Suspension Reason",
        index=True,
    )
    suspended_reason_category_id = fields.Many2one(
        "contract.automatic.invoice.suspension.reason",
        compute="_compute_suspended_reason_category_id",
        string="Auto Invoice Suspension Reason Category",
        store=True,
        index=True,
        recursive=True,
    )
    can_be_selected = fields.Boolean(default=True)
    company_id = fields.Many2one(
        comodel_name="res.company", default=lambda self: self.env.company
    )

    @api.constrains("parent_id")
    def check_parent_different_from_self(self):
        if self._has_cycle("parent_id"):
            raise ValidationError(
                _("There cannot be a recursion in Suspension Reason Hierarchy")
            )

    def _compute_display_name(self):
        for rec in self:
            if rec.parent_id:
                rec.display_name = f"{rec.parent_id.name} - {rec.name}"
            else:
                rec.display_name = rec.name

    @api.depends("parent_id.suspended_reason_category_id")
    def _compute_suspended_reason_category_id(self):
        self.env.cr.execute(
            """
            WITH RECURSIVE trid(id, parent_id,
            suspended_reason_category_id, final) AS (
                SELECT
                    id, parent_id, id,
                    (parent_id IS NULL) as final
                FROM contract_automatic_invoice_suspension_reason
                WHERE id = ANY(%s)
            UNION
                SELECT
                    trid.id, ctr.parent_id, ctr.id,
                    (ctr.parent_id IS NULL) as final
                FROM contract_automatic_invoice_suspension_reason ctr
                JOIN trid ON (trid.parent_id = ctr.id)
                WHERE NOT trid.final
            )
            SELECT trid.id, trid.suspended_reason_category_id
            FROM trid
            WHERE final AND id = ANY(%s);
            """,
            [self.ids, self.ids],
        )

        d = dict(self.env.cr.fetchall())
        for suspension_reason in self:
            fetched = d.get(suspension_reason.id)
            if fetched is not None:
                suspension_reason.suspended_reason_category_id = fetched
            elif not suspension_reason.parent_id:
                suspension_reason.suspended_reason_category_id = suspension_reason
            else:
                suspension_reason.suspended_reason_category_id = (
                    suspension_reason.parent_id.suspended_reason_category_id
                )
