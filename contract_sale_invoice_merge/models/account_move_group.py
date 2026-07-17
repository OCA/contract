# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import Command, api, fields, models

from odoo.addons.account.models.account_move import AccountMove

from .account_move_group_mixin import AccountMoveGroupMixin


class AccountMoveGroup(models.TransientModel):
    _name = "account.move.group"
    _description = "Account Move Group"

    partner_invoice_id = fields.Many2one(comodel_name="res.partner")
    payment_term_id = fields.Many2one(comodel_name="account.payment.term")
    user_id = fields.Many2one(comodel_name="res.users")
    fiscal_position_id = fields.Many2one(comodel_name="account.fiscal.position")
    journal_id = fields.Many2one(comodel_name="account.journal")

    @api.model
    def _get_groupable_models(self):
        return list(self.env["account.move.group.mixin"]._inherit_children)

    def _get_groups_by_recordset(self, date_ref):
        groups = {}

        for model_name in self._get_groupable_models():
            Model = self.env[model_name]
            if not isinstance(Model, AccountMoveGroupMixin):
                continue

            domain = Model._get_group_invoice_domain(date_ref)
            records = Model.search(domain=domain)
            for rec in records:
                if rec.do_not_group_move:
                    # Create separate groups for records that cannot be grouped
                    groups[model_name + str(rec.id)] = {model_name: rec}

                grouping_vals = rec._get_invoice_grouping_dict()
                grouping_key = tuple(sorted(grouping_vals.items()))
                if grouping_key not in groups:
                    # Initialize empty recordsets for all registered models
                    groups[grouping_key] = {
                        m: self.env[m] for m in self._get_groupable_models()
                    }

                groups[grouping_key][model_name] |= rec

        return groups

    def _set_move_line_origins(self, invoices_values):
        for invoice_values in invoices_values:
            invoice_origin = invoice_values.get("invoice_origin")
            for inv_line in invoice_values.get("invoice_line_ids", []):
                # Fill in origin into every invoice line.
                inv_line[2]["origin"] = f"{invoice_origin}" if invoice_origin else ""
        return invoices_values

    @api.model
    def _merge_invoices_values(self, invoices_values, date_ref=False):
        """
        This method merges the given invoices values list into one.
        All invoices are merged into the first one of the list.
        :param invoices_values: list of dictionaries (invoices values)
        :return: list containing the dictionary of values of the result invoice
        """
        if not invoices_values:
            return []
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        init_vals = invoices_values[0]
        init_vals.update({"invoice_date": date_ref})
        for invoice_values in invoices_values[1:]:
            # Merge invoice lines
            for inv_line in invoice_values.get("invoice_line_ids", []):
                init_vals.setdefault("invoice_line_ids", [])
                # Ignore tuples that would empty the set of lines
                if inv_line == Command.set([]):
                    continue
                init_vals["invoice_line_ids"].append(inv_line)
            # Merge origin
            init_origin = init_vals.get("invoice_origin", "")
            invoice_origin = invoice_values.get("invoice_origin")
            if invoice_origin:
                init_vals["invoice_origin"] = f"{init_origin}, {invoice_origin}"
        return init_vals

    def _get_grouped_invoice_vals(self, group_records, date_ref):
        invoices_vals = []
        for model in group_records.values():
            invoices_vals += model._prepare_group_invoices_values(date_ref)

        invoice_vals_origin = self._set_move_line_origins(invoices_vals)

        final_invoice_vals = self._merge_invoices_values(invoice_vals_origin, date_ref)
        return final_invoice_vals

    def _post_create_group_invoices(
        self, models: AccountMoveGroupMixin, moves: AccountMove
    ):
        for model in models:
            model._hook_post_create_group_invoices(moves)

    def _create_grouped_invoice(self, group_records, date_ref):
        invoices_vals = self._get_grouped_invoice_vals(group_records, date_ref)
        invoices = self.env["account.move"].create(invoices_vals)
        if invoices:
            self._post_create_group_invoices(group_records.values(), invoices)
        return invoices

    @api.model
    def _cron_group_recurring_create_invoice(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        groups = self._get_groups_by_recordset(date_ref)
        for _grouping_key, group_records in groups.items():
            self.with_delay()._job_create_grouped_invoice(group_records, date_ref)

    @api.model
    def _job_create_grouped_invoice(self, group_records, date_ref):
        invoices = self.env["account.move"]
        while True:
            created_invoice = self._create_grouped_invoice(group_records, date_ref)
            if not created_invoice:
                break
            invoices |= created_invoice
        return invoices

    @api.model
    def cron_group_recurring_create_invoice(self):
        return self._cron_group_recurring_create_invoice()
