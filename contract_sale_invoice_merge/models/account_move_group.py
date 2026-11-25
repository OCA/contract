# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import defaultdict

from dateutil.relativedelta import relativedelta

from odoo import Command, api, fields, models

from odoo.addons.account.models.account_move import AccountMove

from .account_move_group_mixin import AccountMoveGroupMixin


class AccountMoveGroup(models.Model):
    _name = "account.move.group"
    _description = "Account Move Group"

    grouping_key = fields.Char()

    contract_ids = fields.Many2many(
        comodel_name="contract.contract",
        string="Related Contracts",
    )
    sale_order_ids = fields.Many2many(
        comodel_name="sale.order",
        string="Related Sale Orders",
    )

    @api.model
    def _get_groupable_models(self):
        return list(self.env["account.move.group.mixin"]._inherit_children)

    @api.model
    def _get_groupable_model_field_mapping(self):
        return {
            "sale.order": "sale_order_ids",
            "contract.contract": "contract_ids",
        }

    @api.model
    def _create_account_move_groups(self, date_ref=None, groups=None):
        if not groups:
            groups = self._search_groups_by_recordset(date_ref)
        # Create account.move.group for each group
        model_field_map = self._get_groupable_model_field_mapping()
        account_move_groups = self.browse()
        for grouping_key, group_model in groups.items():
            create_vals = {"grouping_key": grouping_key}
            for model, records in group_model.items():
                field_name = model_field_map[model]
                create_vals[field_name] = records

            account_move_groups += self.create(create_vals)

        return account_move_groups

    @api.model
    def _search_groups_by_recordset(self, date_ref):
        """Search for invoiceable lines and group them according to grouping dict.

        :return: Groups in the following format
        {grouping_key: {model: records}}
        Ex.: {((user_id, 1)): {"sale.order": SaleOrder(1,2,)}}
        """
        groupable_models = self._get_groupable_models()

        def default_group():
            return {m: self.env[m] for m in groupable_models}

        groups = defaultdict(default_group)

        for model_name in groupable_models:
            Model = self.env[model_name]
            if not isinstance(Model, AccountMoveGroupMixin):
                continue

            domain = Model._get_group_invoice_domain(date_ref)
            records = Model.search(domain=domain)
            for rec in records:
                if rec.do_not_group_move:
                    # Create separate groups for records that cannot be grouped
                    groups[f"{model_name}_{rec.id}"] = {model_name: rec}
                    continue

                grouping_vals = rec._get_group_invoice_dict()
                grouping_key = tuple(sorted(grouping_vals.items()))
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

    def _get_grouped_invoice_vals(self, date_ref):
        invoices_vals = []
        model_field_map = self._get_groupable_model_field_mapping()
        for _model_name, field in model_field_map.items():
            records: AccountMoveGroupMixin = self[field]
            invoices_vals += records._get_group_invoice_values(date_ref)

        invoice_vals_origin = self._set_move_line_origins(invoices_vals)

        final_invoice_vals = self._merge_invoices_values(invoice_vals_origin, date_ref)
        return final_invoice_vals

    def _post_create_group_invoices(self, moves: AccountMove):
        model_field_map = self._get_groupable_model_field_mapping()
        for _model_name, field in model_field_map.items():
            records: AccountMoveGroupMixin = self[field]
            records._hook_post_create_group_invoices(moves)

    def _create_grouped_invoice(self, date_ref):
        invoices_vals = self._get_grouped_invoice_vals(date_ref)
        invoices = self.env["account.move"].create(invoices_vals)
        if invoices:
            self._post_create_group_invoices(moves=invoices)
        return invoices

    @api.model
    def _cron_group_recurring_create_invoice(self, date_ref=None):
        if not date_ref:
            date_ref = fields.Date.context_today(self)
        account_move_groups = self._create_account_move_groups(date_ref)
        for group in account_move_groups:
            group.with_delay()._job_create_grouped_invoice(date_ref)

    def _job_create_grouped_invoice(self, date_ref, action_post=True):
        invoices = self.env["account.move"]
        while True:
            created_invoice = self._create_grouped_invoice(date_ref)
            if not created_invoice:
                break
            invoices |= created_invoice
        if action_post:
            invoices.action_post()
        return invoices

    GC_CHUNK_SIZE = 500
    GC_DELAY = relativedelta(months=1)

    @api.autovacuum
    def _gc_account_move_group(self):
        now = fields.Datetime.now()

        ids = self.search([("create_date", "<", now - self.GC_DELAY)]).ids
        for i in range(0, len(ids), self.GC_CHUNK_SIZE):
            chunk_ids = ids[i : i + self.GC_CHUNK_SIZE]
            self.with_delay()._job_gc_chunk(chunk_ids)

    def _job_gc_chunk(self, ids):
        records = self.browse(ids).exists()
        records.unlink()
