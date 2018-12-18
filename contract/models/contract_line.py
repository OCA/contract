# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .contract_line_constraints import get_allowed


class AccountAnalyticInvoiceLine(models.Model):
    _name = 'account.analytic.invoice.line'
    _inherit = 'account.abstract.analytic.contract.line'

    contract_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Contract',
        required=True,
        index=True,
        ondelete='cascade',
        oldname='analytic_account_id',
    )
    date_start = fields.Date(
        string='Date Start',
        required=True,
        default=lambda self: fields.Date.context_today(self),
    )
    date_end = fields.Date(string='Date End', index=True)
    recurring_next_date = fields.Date(string='Date of Next Invoice')
    last_date_invoiced = fields.Date(
        string='Last Date Invoiced', readonly=True, copy=False
    )
    create_invoice_visibility = fields.Boolean(
        compute='_compute_create_invoice_visibility'
    )
    successor_contract_line_id = fields.Many2one(
        comodel_name='account.analytic.invoice.line',
        string="Successor Contract Line",
        required=False,
        readonly=True,
        copy=False,
        help="In case of restart after suspension, this field contain the new "
        "contract line created.",
    )
    predecessor_contract_line_id = fields.Many2one(
        comodel_name='account.analytic.invoice.line',
        string="Predecessor Contract Line",
        required=False,
        readonly=True,
        copy=False,
        help="Contract Line origin of this one.",
    )
    is_plan_successor_allowed = fields.Boolean(
        string="Plan successor allowed?", compute='_compute_allowed'
    )
    is_stop_plan_successor_allowed = fields.Boolean(
        string="Stop/Plan successor allowed?", compute='_compute_allowed'
    )
    is_stop_allowed = fields.Boolean(
        string="Stop allowed?", compute='_compute_allowed'
    )
    is_cancel_allowed = fields.Boolean(
        string="Cancel allowed?", compute='_compute_allowed'
    )
    is_un_cancel_allowed = fields.Boolean(
        string="Un-Cancel allowed?", compute='_compute_allowed'
    )
    state = fields.Selection(
        string="State",
        selection=[
            ('upcoming', 'Upcoming'),
            ('in-progress', 'In-progress'),
            ('upcoming-close', 'Upcoming Close'),
            ('closed', 'Closed'),
            ('canceled', 'Canceled'),
        ],
        compute="_compute_state",
    )
    active = fields.Boolean(
        string="Active",
        related="contract_id.active",
        store=True,
        readonly=True,
    )

    @api.multi
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_start:
                if rec.is_canceled:
                    rec.state = 'canceled'
                elif today < rec.date_start:
                    rec.state = 'upcoming'
                elif not rec.date_end or (
                    today <= rec.date_end and rec.is_auto_renew
                ):
                    rec.state = 'in-progress'
                elif today <= rec.date_end and not rec.is_auto_renew:
                    rec.state = 'upcoming-close'
                else:
                    rec.state = 'closed'

    @api.depends(
        'date_start',
        'date_end',
        'last_date_invoiced',
        'is_auto_renew',
        'successor_contract_line_id',
        'predecessor_contract_line_id',
        'is_canceled',
    )
    def _compute_allowed(self):
        for rec in self:
            if rec.date_start:
                allowed = get_allowed(
                    rec.date_start,
                    rec.date_end,
                    rec.last_date_invoiced,
                    rec.is_auto_renew,
                    rec.successor_contract_line_id,
                    rec.predecessor_contract_line_id,
                    rec.is_canceled,
                )
                if allowed:
                    rec.is_plan_successor_allowed = allowed.plan_successor
                    rec.is_stop_plan_successor_allowed = (
                        allowed.stop_plan_successor
                    )
                    rec.is_stop_allowed = allowed.stop
                    rec.is_cancel_allowed = allowed.cancel
                    rec.is_un_cancel_allowed = allowed.uncancel

    @api.constrains('is_auto_renew', 'successor_contract_line_id', 'date_end')
    def _check_allowed(self):
        """
            logical impossible combination:
                * a line with is_auto_renew True should have date_end and
                  couldn't have successor_contract_line_id
                * a line without date_end can't have successor_contract_line_id

        """
        for rec in self:
            if rec.is_auto_renew:
                if rec.successor_contract_line_id:
                    raise ValidationError(
                        _(
                            "A contract line with a successor "
                            "can't be set to auto-renew"
                        )
                    )
                if not rec.date_end:
                    raise ValidationError(
                        _("An auto-renew line must have a end date")
                    )
            else:
                if not rec.date_end and rec.successor_contract_line_id:
                    raise ValidationError(
                        _(
                            "A contract line with a successor "
                            "must have a end date"
                        )
                    )

    @api.constrains('successor_contract_line_id', 'date_end')
    def _check_overlap_successor(self):
        for rec in self:
            if rec.date_end and rec.successor_contract_line_id:
                if rec.date_end >= rec.successor_contract_line_id.date_start:
                    raise ValidationError(
                        _("Contract line and its successor overlapped")
                    )

    @api.constrains('predecessor_contract_line_id', 'date_start')
    def _check_overlap_predecessor(self):
        for rec in self:
            if rec.predecessor_contract_line_id:
                if rec.date_start <= rec.predecessor_contract_line_id.date_end:
                    raise ValidationError(
                        _("Contract line and its predecessor overlapped")
                    )

    @api.model
    def _compute_first_recurring_next_date(
        self,
        date_start,
        recurring_invoicing_type,
        recurring_rule_type,
        recurring_interval,
    ):
        if recurring_rule_type == 'monthlylastday':
            return date_start + self.get_relative_delta(
                recurring_rule_type, recurring_interval - 1
            )
        if recurring_invoicing_type == 'pre-paid':
            return date_start
        return date_start + self.get_relative_delta(
            recurring_rule_type, recurring_interval
        )

    @api.onchange(
        'date_start',
        'is_auto_renew',
        'auto_renew_rule_type',
        'auto_renew_interval',
    )
    def _onchange_is_auto_renew(self):
        """Date end should be auto-computed if a contract line is set to
        auto_renew"""
        for rec in self.filtered('is_auto_renew'):
            if rec.date_start:
                rec.date_end = (
                    self.date_start
                    + self.get_relative_delta(
                        rec.auto_renew_rule_type, rec.auto_renew_interval
                    )
                    - relativedelta(days=1)
                )

    @api.onchange(
        'date_start',
        'recurring_invoicing_type',
        'recurring_rule_type',
        'recurring_interval',
    )
    def _onchange_date_start(self):
        for rec in self.filtered('date_start'):
            rec.recurring_next_date = self._compute_first_recurring_next_date(
                rec.date_start,
                rec.recurring_invoicing_type,
                rec.recurring_rule_type,
                rec.recurring_interval,
            )

    @api.constrains('recurring_next_date', 'date_start')
    def _check_recurring_next_date_start_date(self):
        for line in self.filtered('recurring_next_date'):
            if line.date_start and line.recurring_next_date:
                if line.date_start > line.recurring_next_date:
                    raise ValidationError(
                        _(
                            "You can't have a date of next invoice anterior "
                            "to the start of the contract line '%s'"
                        )
                        % line.name
                    )

    @api.constrains('date_start', 'date_end', 'last_date_invoiced')
    def _check_last_date_invoiced(self):
        for rec in self.filtered('last_date_invoiced'):
            if rec.date_start and rec.date_start > rec.last_date_invoiced:
                raise ValidationError(
                    _(
                        "You can't have the start date after the date of last "
                        "invoice for the contract line '%s'"
                    )
                    % rec.name
                )
            if rec.date_end and rec.date_end < rec.last_date_invoiced:
                raise ValidationError(
                    _(
                        "You can't have the end date before the date of last "
                        "invoice for the contract line '%s'"
                    )
                    % rec.name
                )

    @api.constrains('recurring_next_date')
    def _check_recurring_next_date_recurring_invoices(self):
        for rec in self.filtered('contract_id.recurring_invoices'):
            if not rec.recurring_next_date and (
                not rec.last_date_invoiced
                or rec.last_date_invoiced < rec.date_end
            ):
                raise ValidationError(
                    _(
                        "You must supply a date of next invoice for contract "
                        "line '%s'"
                    )
                    % rec.name
                )

    @api.constrains('date_start')
    def _check_date_start_recurring_invoices(self):
        for line in self.filtered('contract_id.recurring_invoices'):
            if not line.date_start:
                raise ValidationError(
                    _("You must supply a start date for contract line '%s'")
                    % line.name
                )

    @api.constrains('date_start', 'date_end')
    def _check_start_end_dates(self):
        for line in self.filtered('date_end'):
            if line.date_start and line.date_end:
                if line.date_start > line.date_end:
                    raise ValidationError(
                        _(
                            "Contract line '%s' start date can't be later than"
                            " end date"
                        )
                        % line.name
                    )

    @api.depends('recurring_next_date', 'date_start', 'date_end')
    def _compute_create_invoice_visibility(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.date_start:
                if today < rec.date_start:
                    rec.create_invoice_visibility = False
                else:
                    rec.create_invoice_visibility = bool(
                        rec.recurring_next_date
                    )

    @api.multi
    def _prepare_invoice_line(self, invoice_id=False):
        self.ensure_one()
        invoice_line_vals = {
            'product_id': self.product_id.id,
            'quantity': self.quantity,
            'uom_id': self.uom_id.id,
            'discount': self.discount,
        }
        if invoice_id:
            invoice_line_vals['invoice_id'] = invoice_id.id
        invoice_line = self.env['account.invoice.line'].new(invoice_line_vals)
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        # Insert markers
        contract = self.contract_id
        first_date_invoiced, last_date_invoiced = self._get_invoiced_period()
        name = self._insert_markers(first_date_invoiced, last_date_invoiced)
        invoice_line_vals.update(
            {
                'name': name,
                'account_analytic_id': contract.id,
                'price_unit': self.price_unit,
            }
        )
        return invoice_line_vals

    @api.multi
    def _get_invoiced_period(self):
        self.ensure_one()
        first_date_invoiced = (
            self.last_date_invoiced + relativedelta(days=1)
            if self.last_date_invoiced
            else self.date_start
        )
        if self.recurring_rule_type == 'monthlylastday':
            last_date_invoiced = self.recurring_next_date
        else:
            if self.recurring_invoicing_type == 'pre-paid':
                last_date_invoiced = (
                    self.recurring_next_date
                    + self.get_relative_delta(
                        self.recurring_rule_type, self.recurring_interval
                    )
                    - relativedelta(days=1)
                )
            else:
                last_date_invoiced = self.recurring_next_date - relativedelta(
                    days=1
                )
        if self.date_end and self.date_end < last_date_invoiced:
            last_date_invoiced = self.date_end
        return first_date_invoiced, last_date_invoiced

    @api.multi
    def _insert_markers(self, first_date_invoiced, last_date_invoiced):
        self.ensure_one()
        lang_obj = self.env['res.lang']
        lang = lang_obj.search(
            [('code', '=', self.contract_id.partner_id.lang)]
        )
        date_format = lang.date_format or '%m/%d/%Y'
        name = self.name
        name = name.replace(
            '#START#', first_date_invoiced.strftime(date_format)
        )
        name = name.replace('#END#', last_date_invoiced.strftime(date_format))
        return name

    @api.multi
    def _update_recurring_next_date(self):
        for rec in self:
            old_date = rec.recurring_next_date
            new_date = old_date + self.get_relative_delta(
                rec.recurring_rule_type, rec.recurring_interval
            )

            if rec.recurring_rule_type == 'monthlylastday':
                rec.last_date_invoiced = (
                    old_date
                    if rec.date_end and old_date < rec.date_end
                    else rec.date_end
                )
            elif rec.recurring_invoicing_type == 'post-paid':
                rec.last_date_invoiced = (
                    old_date - relativedelta(days=1)
                    if rec.date_end and old_date < rec.date_end
                    else rec.date_end
                )
            elif rec.recurring_invoicing_type == 'pre-paid':
                rec.last_date_invoiced = (
                    new_date - relativedelta(days=1)
                    if rec.date_end and new_date < rec.date_end
                    else rec.date_end
                )
            if (
                rec.last_date_invoiced
                and rec.last_date_invoiced == rec.date_end
            ):
                rec.recurring_next_date = False
            else:
                rec.recurring_next_date = new_date

    @api.multi
    def _init_last_date_invoiced(self):
        """Used to init last_date_invoiced for migration purpose"""
        for rec in self:
            if rec.recurring_rule_type == 'monthlylastday':
                last_date_invoiced = (
                    rec.recurring_next_date
                    - self.get_relative_delta(
                        rec.recurring_rule_type, rec.recurring_interval
                    )
                )
            elif rec.recurring_invoicing_type == 'post-paid':
                last_date_invoiced = (
                    rec.recurring_next_date
                    - self.get_relative_delta(
                        rec.recurring_rule_type, rec.recurring_interval
                    )
                ) - relativedelta(days=1)
            if last_date_invoiced > rec.date_start:
                rec.last_date_invoiced = last_date_invoiced

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        if recurring_rule_type == 'daily':
            return relativedelta(days=interval)
        elif recurring_rule_type == 'weekly':
            return relativedelta(weeks=interval)
        elif recurring_rule_type == 'monthly':
            return relativedelta(months=interval)
        elif recurring_rule_type == 'monthlylastday':
            return relativedelta(months=interval, day=31)
        else:
            return relativedelta(years=interval)

    @api.multi
    def _delay(self, delay_delta):
        """
        Delay a contract line
        :param delay_delta: delay relative delta
        :return: delayed contract line
        """
        for rec in self:
            if rec.last_date_invoiced:
                raise ValidationError(
                    _(
                        "You can't delay a contract line "
                        "invoiced at least one time."
                    )
                )
            new_date_start = rec.date_start + delay_delta
            rec.recurring_next_date = self._compute_first_recurring_next_date(
                new_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_rule_type,
                rec.recurring_interval,
            )
            if rec.date_end:
                rec.date_end += delay_delta
            rec.date_start = new_date_start

    @api.multi
    def stop(self, date_end, post_message=True):
        """
        Put date_end on contract line
        We don't consider contract lines that end's before the new end date
        :param date_end: new date end for contract line
        :return: True
        """
        if not all(self.mapped('is_stop_allowed')):
            raise ValidationError(_('Stop not allowed for this line'))
        for rec in self:
            if date_end < rec.date_start:
                rec.cancel()
            else:
                if not rec.date_end or rec.date_end > date_end:
                    if post_message:
                        old_date_end = rec.date_end
                        msg = _(
                            """Contract line for <strong>{product}</strong>
                            stopped: <br/>
                            - <strong>End</strong>: {old_end} -- {new_end}
                            """.format(
                                product=rec.name,
                                old_end=old_date_end,
                                new_end=rec.date_end,
                            )
                        )
                        rec.contract_id.message_post(body=msg)
                    rec.write({'date_end': date_end, 'is_auto_renew': False})
                else:
                    rec.write({'is_auto_renew': False})
        return True

    @api.multi
    def _prepare_value_for_plan_successor(
        self, date_start, date_end, is_auto_renew, recurring_next_date=False
    ):
        self.ensure_one()
        if not recurring_next_date:
            recurring_next_date = self._compute_first_recurring_next_date(
                date_start,
                self.recurring_invoicing_type,
                self.recurring_rule_type,
                self.recurring_interval,
            )
        new_vals = self.read()[0]
        new_vals.pop("id", None)
        values = self._convert_to_write(new_vals)
        values['date_start'] = date_start
        values['date_end'] = date_end
        values['recurring_next_date'] = recurring_next_date
        values['is_auto_renew'] = is_auto_renew
        values['predecessor_contract_line_id'] = self.id
        return values

    @api.multi
    def plan_successor(
        self,
        date_start,
        date_end,
        is_auto_renew,
        recurring_next_date=False,
        post_message=True,
    ):
        """
        Create a copy of a contract line in a new interval
        :param date_start: date_start for the successor_contract_line
        :param date_end: date_end for the successor_contract_line
        :param is_auto_renew: is_auto_renew option for successor_contract_line
        :param recurring_next_date: recurring_next_date for the
        successor_contract_line
        :return: successor_contract_line
        """
        contract_line = self.env['account.analytic.invoice.line']
        for rec in self:
            if not rec.is_plan_successor_allowed:
                raise ValidationError(
                    _('Plan successor not allowed for this line')
                )
            rec.is_auto_renew = False
            new_line = self.create(
                rec._prepare_value_for_plan_successor(
                    date_start, date_end, is_auto_renew, recurring_next_date
                )
            )
            rec.successor_contract_line_id = new_line
            contract_line |= new_line
            if post_message:
                msg = _(
                    """Contract line for <strong>{product}</strong>
                    planned a successor: <br/>
                    - <strong>Start</strong>: {new_date_start}
                    <br/>
                    - <strong>End</strong>: {new_date_end}
                    """.format(
                        product=rec.name,
                        new_date_start=new_line.date_start,
                        new_date_end=new_line.date_end,
                    )
                )
                rec.contract_id.message_post(body=msg)
        return contract_line

    @api.multi
    def stop_plan_successor(self, date_start, date_end, is_auto_renew):
        """
        Stop a contract line for a defined period and start it later
        Cases to consider:
            * contract line end's before the suspension period:
                -> apply stop
            * contract line start before the suspension period and end in it
                -> apply stop at suspension start date
                -> apply plan successor:
                    - date_start: suspension.date_end
                    - date_end: date_end    + (contract_line.date_end
                                            - suspension.date_start)
            * contract line start before the suspension period and end after it
                -> apply stop at suspension start date
                -> apply plan successor:
                    - date_start: suspension.date_end
                    - date_end: date_end + (suspension.date_end
                                        - suspension.date_start)
            * contract line start and end's in the suspension period
                -> apply delay
                    - delay: suspension.date_end - contract_line.date_start
            * contract line start in the suspension period and end after it
                -> apply delay
                    - delay: suspension.date_end - contract_line.date_start
            * contract line start  and end after the suspension period
                -> apply delay
                    - delay: suspension.date_end - suspension.start_date
        :param date_start: suspension start date
        :param date_end: suspension end date
        :param is_auto_renew: is the new line is set to auto_renew
        :return: created contract line
        """
        if not all(self.mapped('is_stop_plan_successor_allowed')):
            raise ValidationError(
                _('Stop/Plan successor not allowed for this line')
            )
        contract_line = self.env['account.analytic.invoice.line']
        for rec in self:
            if rec.date_start >= date_start:
                if rec.date_start < date_end:
                    delay = (date_end - rec.date_start) + timedelta(days=1)
                else:
                    delay = (date_end - date_start) + timedelta(days=1)
                rec._delay(delay)
                contract_line |= rec
            else:
                if rec.date_end and rec.date_end < date_start:
                    rec.stop(date_start, post_message=False)
                elif (
                    rec.date_end
                    and rec.date_end > date_start
                    and rec.date_end < date_end
                ):
                    new_date_start = date_end + relativedelta(days=1)
                    new_date_end = (
                        date_end
                        + (rec.date_end - date_start)
                        + relativedelta(days=1)
                    )
                    rec.stop(
                        date_start - relativedelta(days=1), post_message=False
                    )
                    contract_line |= rec.plan_successor(
                        new_date_start,
                        new_date_end,
                        is_auto_renew,
                        post_message=False,
                    )
                else:
                    new_date_start = date_end + relativedelta(days=1)
                    if rec.date_end:
                        new_date_end = (
                            rec.date_end
                            + (date_end - date_start)
                            + relativedelta(days=1)
                        )
                    else:
                        new_date_end = rec.date_end

                    rec.stop(
                        date_start - relativedelta(days=1), post_message=False
                    )
                    contract_line |= rec.plan_successor(
                        new_date_start,
                        new_date_end,
                        is_auto_renew,
                        post_message=False,
                    )
            msg = _(
                """Contract line for <strong>{product}</strong>
                suspended: <br/>
                - <strong>Suspension Start</strong>: {new_date_start}
                <br/>
                - <strong>Suspension End</strong>: {new_date_end}
                """.format(
                    product=rec.name,
                    new_date_start=date_start,
                    new_date_end=date_end,
                )
            )
            rec.contract_id.message_post(body=msg)
        return contract_line

    @api.multi
    def cancel(self):
        if not all(self.mapped('is_cancel_allowed')):
            raise ValidationError(_('Cancel not allowed for this line'))
        for contract in self.mapped('contract_id'):
            lines = self.filtered(lambda l, c=contract: l.contract_id == c)
            msg = _(
                """Contract line canceled: %s"""
                % "<br/>- ".join(
                    [
                        "<strong>%s</strong>" % name
                        for name in lines.mapped('name')
                    ]
                )
            )
            contract.message_post(body=msg)
        self.mapped('predecessor_contract_line_id').write(
            {'successor_contract_line_id': False}
        )
        return self.write({'is_canceled': True})

    @api.multi
    def uncancel(self, recurring_next_date):
        if not all(self.mapped('is_un_cancel_allowed')):
            raise ValidationError(_('Un-cancel not allowed for this line'))
        for contract in self.mapped('contract_id'):
            lines = self.filtered(lambda l, c=contract: l.contract_id == c)
            msg = _(
                """Contract line Un-canceled: %s"""
                % "<br/>- ".join(
                    [
                        "<strong>%s</strong>" % name
                        for name in lines.mapped('name')
                    ]
                )
            )
            contract.message_post(body=msg)
        for rec in self:
            if rec.predecessor_contract_line_id:
                rec.predecessor_contract_line_id.successor_contract_line_id = (
                    rec
                )
            rec.is_canceled = False
            rec.recurring_next_date = recurring_next_date
        return True

    @api.multi
    def action_uncancel(self):
        self.ensure_one()
        context = {
            'default_contract_line_id': self.id,
            'default_recurring_next_date': fields.Date.context_today(self),
        }
        context.update(self.env.context)
        view_id = self.env.ref(
            'contract.contract_line_wizard_uncancel_form_view'
        ).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Un-Cancel Contract Line',
            'res_model': 'account.analytic.invoice.line.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }

    @api.multi
    def action_plan_successor(self):
        self.ensure_one()
        context = {
            'default_contract_line_id': self.id,
            'default_is_auto_renew': self.is_auto_renew,
        }
        context.update(self.env.context)
        view_id = self.env.ref(
            'contract.contract_line_wizard_plan_successor_form_view'
        ).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Plan contract line successor',
            'res_model': 'account.analytic.invoice.line.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }

    @api.multi
    def action_stop(self):
        self.ensure_one()
        context = {
            'default_contract_line_id': self.id,
            'default_date_end': self.date_end,
        }
        context.update(self.env.context)
        view_id = self.env.ref(
            'contract.contract_line_wizard_stop_form_view'
        ).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Resiliate contract line',
            'res_model': 'account.analytic.invoice.line.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }

    @api.multi
    def action_stop_plan_successor(self):
        self.ensure_one()
        context = {
            'default_contract_line_id': self.id,
            'default_is_auto_renew': self.is_auto_renew,
        }
        context.update(self.env.context)
        view_id = self.env.ref(
            'contract.contract_line_wizard_stop_plan_successor_form_view'
        ).id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Suspend contract line',
            'res_model': 'account.analytic.invoice.line.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }

    @api.multi
    def _get_renewal_dates(self):
        self.ensure_one()
        date_start = self.date_end + relativedelta(days=1)
        date_end = (
            date_start
            + self.get_relative_delta(
                self.auto_renew_rule_type, self.auto_renew_interval
            )
            - relativedelta(days=1)
        )
        return date_start, date_end

    @api.multi
    def renew(self):
        res = self.env['account.analytic.invoice.line']
        for rec in self:
            is_auto_renew = rec.is_auto_renew
            rec.stop(rec.date_end, post_message=False)
            date_start, date_end = rec._get_renewal_dates()
            new_line = rec.plan_successor(
                date_start, date_end, is_auto_renew, post_message=False
            )
            new_line._onchange_date_start()
            res |= new_line
            msg = _(
                """Contract line for <strong>{product}</strong>
                renewed: <br/>
                - <strong>Start</strong>: {new_date_start}
                <br/>
                - <strong>End</strong>: {new_date_end}
                """.format(
                    product=rec.name,
                    new_date_start=date_start,
                    new_date_end=date_end,
                )
            )
            rec.contract_id.message_post(body=msg)
        return res

    @api.model
    def _contract_line_to_renew_domain(self):
        date_ref = fields.Date.context_today(self) + self.get_relative_delta(
            self.termination_notice_rule_type, self.termination_notice_interval
        )
        return [
            ('is_auto_renew', '=', True),
            ('date_end', '<=', date_ref),
            ('is_canceled', '=', False),
        ]

    @api.model
    def cron_renew_contract_line(self):
        domain = self._contract_line_to_renew_domain()
        to_renew = self.search(domain)
        to_renew.renew()

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        default_contract_type = self.env.context.get('default_contract_type')
        if view_type == 'tree' and default_contract_type == 'purchase':
            view_id = self.env.ref(
                'contract.account_analytic_invoice_line_purchase_view_tree'
            ).id
        if view_type == 'form':
            if default_contract_type == 'purchase':
                view_id = self.env.ref(
                    'contract.account_analytic_invoice_line_purchase_view_form'
                ).id
            elif default_contract_type == 'sale':
                view_id = self.env.ref(
                    'contract.account_analytic_invoice_line_sale_view_form'
                ).id
        return super(AccountAnalyticInvoiceLine, self).fields_view_get(
            view_id, view_type, toolbar, submenu
        )

    @api.multi
    def unlink(self):
        """stop unlink uncnacled lines"""
        if not all(self.mapped('is_canceled')):
            raise ValidationError(
                _("Contract line must be canceled before delete")
            )
        return super(AccountAnalyticInvoiceLine, self).unlink()
