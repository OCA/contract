# Copyright 2017 LasLabs Inc.
# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from .contract_line_constraints import get_allowed


class ContractLine(models.Model):
    _name = 'contract.line'
    _description = "Contract Line"
    _inherit = 'contract.abstract.contract.line'
    _order = 'sequence,id'

    sequence = fields.Integer(
        string="Sequence",
    )
    contract_id = fields.Many2one(
        comodel_name='contract.contract',
        string='Contract',
        required=True,
        index=True,
        auto_join=True,
        ondelete='cascade',
    )
    analytic_account_id = fields.Many2one(
        string="Analytic account",
        comodel_name='account.analytic.account',
    )
    analytic_tag_ids = fields.Many2many(
        comodel_name='account.analytic.tag',
        string='Analytic Tags',
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
    next_period_date_start = fields.Date(
        string='Next Period Start',
        compute='_compute_next_period_date_start',
    )
    next_period_date_end = fields.Date(
        string='Next Period End',
        compute='_compute_next_period_date_end',
    )
    termination_notice_date = fields.Date(
        string='Termination notice date',
        compute="_compute_termination_notice_date",
        store=True,
        copy=False,
    )
    create_invoice_visibility = fields.Boolean(
        compute='_compute_create_invoice_visibility'
    )
    successor_contract_line_id = fields.Many2one(
        comodel_name='contract.line',
        string="Successor Contract Line",
        required=False,
        readonly=True,
        index=True,
        copy=False,
        help="In case of restart after suspension, this field contain the new "
        "contract line created.",
    )
    predecessor_contract_line_id = fields.Many2one(
        comodel_name='contract.line',
        string="Predecessor Contract Line",
        required=False,
        readonly=True,
        index=True,
        copy=False,
        help="Contract Line origin of this one.",
    )
    manual_renew_needed = fields.Boolean(
        string="Manual renew needed",
        default=False,
        help="This flag is used to make a difference between a definitive stop"
        "and temporary one for which a user is not able to plan a"
        "successor in advance",
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
            ('to-renew', 'To renew'),
            ('upcoming-close', 'Upcoming Close'),
            ('closed', 'Closed'),
            ('canceled', 'Canceled'),
        ],
        compute="_compute_state",
        search='_search_state',
    )
    active = fields.Boolean(
        string="Active",
        related="contract_id.active",
        store=True,
        readonly=True,
        default=True,
    )

    @api.multi
    @api.depends(
        'date_end',
        'termination_notice_rule_type',
        'termination_notice_interval',
    )
    def _compute_termination_notice_date(self):
        for rec in self:
            if rec.date_end:
                rec.termination_notice_date = (
                    rec.date_end
                    - self.get_relative_delta(
                        rec.termination_notice_rule_type,
                        rec.termination_notice_interval,
                    )
                )

    @api.multi
    @api.depends('is_canceled', 'date_start', 'date_end', 'is_auto_renew')
    def _compute_state(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.display_type:
                rec.state = False
                continue
            if rec.is_canceled:
                rec.state = 'canceled'
                continue

            if rec.date_start and rec.date_start > today:
                # Before period
                rec.state = 'upcoming'
                continue
            if (
                rec.date_start
                and rec.date_start <= today
                and (not rec.date_end or rec.date_end >= today)
            ):
                # In period
                if (
                    rec.termination_notice_date
                    and rec.termination_notice_date < today
                    and not rec.is_auto_renew
                    and not rec.manual_renew_needed
                ):
                    rec.state = 'upcoming-close'
                else:
                    rec.state = 'in-progress'
                continue
            if rec.date_end and rec.date_end < today:
                # After
                if (
                    rec.manual_renew_needed
                    and not rec.successor_contract_line_id
                    or rec.is_auto_renew
                ):
                    rec.state = 'to-renew'
                else:
                    rec.state = 'closed'

    @api.model
    def _get_state_domain(self, state):
        today = fields.Date.context_today(self)
        if state == 'upcoming':
            return [
                "&",
                ('date_start', '>', today),
                ('is_canceled', '=', False),
            ]
        if state == 'in-progress':
            return [
                "&",
                "&",
                "&",
                ('display_type', '=', False),
                ('date_start', '<=', today),
                "|",
                ('date_end', '=', False),
                ('date_end', '>=', today),
                "|",
                "|",
                "|",
                ('termination_notice_date', '=', False),
                ('termination_notice_date', '>=', today),
                ('is_auto_renew', '=', True),
                ('manual_renew_needed', '=', True),
            ]
        if state == 'to-renew':
            return [
                "&",
                "&",
                ('is_canceled', '=', False),
                ('date_end', '<', today),
                "|",
                "&",
                ('manual_renew_needed', '=', True),
                ('successor_contract_line_id', '=', False),
                ('is_auto_renew', '=', True),
            ]
        if state == 'upcoming-close':
            return [
                "&",
                "&",
                "&",
                "&",
                "&",
                ('date_start', '<=', today),
                ('is_auto_renew', '=', False),
                ('manual_renew_needed', '=', False),
                ('is_canceled', '=', False),
                ('termination_notice_date', '<', today),
                ('date_end', '>=', today),
            ]
        if state == 'closed':
            return [
                "&",
                "&",
                "&",
                ('is_canceled', '=', False),
                ('date_end', '<', today),
                ('is_auto_renew', '=', False),
                "|",
                "&",
                ('manual_renew_needed', '=', True),
                ('successor_contract_line_id', '!=', False),
                ('manual_renew_needed', '=', False),
            ]
        if state == 'canceled':
            return [('is_canceled', '=', True)]
        if not state:
            return [('display_type', '!=', False)]

    @api.model
    def _search_state(self, operator, value):
        states = [
            'upcoming',
            'in-progress',
            'to-renew',
            'upcoming-close',
            'closed',
            'canceled',
            False,
        ]
        if operator == '=':
            return self._get_state_domain(value)
        if operator == '!=':
            domain = []
            for state in states:
                if state != value:
                    if domain:
                        domain.insert(0, '|')
                    domain.extend(self._get_state_domain(state))
            return domain
        if operator == 'in':
            domain = []
            for state in value:
                if domain:
                    domain.insert(0, '|')
                domain.extend(self._get_state_domain(state))
            return domain

        if operator == 'not in':
            if set(value) == set(states):
                return [('id', '=', False)]
            return self._search_state(
                'in', [state for state in states if state not in value]
            )

    @api.depends(
        'date_start',
        'date_end',
        'last_date_invoiced',
        'is_auto_renew',
        'successor_contract_line_id',
        'predecessor_contract_line_id',
        'is_canceled',
        'contract_id.is_terminated',
    )
    def _compute_allowed(self):
        for rec in self:
            if rec.contract_id.is_terminated:
                rec.update({
                    'is_plan_successor_allowed': False,
                    'is_stop_plan_successor_allowed': False,
                    'is_stop_allowed': False,
                    'is_cancel_allowed': False,
                    'is_un_cancel_allowed': False,
                })
                continue
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
                    rec.update({
                        'is_plan_successor_allowed': allowed.plan_successor,
                        'is_stop_plan_successor_allowed':
                            allowed.stop_plan_successor,
                        'is_stop_allowed': allowed.stop,
                        'is_cancel_allowed': allowed.cancel,
                        'is_un_cancel_allowed': allowed.uncancel,
                    })

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
        recurring_interval
    ):
        # deprecated method for backward compatibility
        return self.get_next_invoice_date(
            date_start,
            recurring_invoicing_type,
            self._get_default_recurring_invoicing_offset(
                recurring_invoicing_type, recurring_rule_type
            ),
            recurring_rule_type,
            recurring_interval,
            max_date_end=False,
        )

    @api.model
    def get_next_invoice_date(
        self,
        next_period_date_start,
        recurring_invoicing_type,
        recurring_invoicing_offset,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
    ):
        next_period_date_end = self.get_next_period_date_end(
            next_period_date_start,
            recurring_rule_type,
            recurring_interval,
            max_date_end=max_date_end,
        )
        if not next_period_date_end:
            return False
        if recurring_invoicing_type == 'pre-paid':
            recurring_next_date = (
                next_period_date_start
                + relativedelta(days=recurring_invoicing_offset)
            )
        else:  # post-paid
            recurring_next_date = (
                next_period_date_end
                + relativedelta(days=recurring_invoicing_offset)
            )
        return recurring_next_date

    @api.model
    def get_next_period_date_end(
        self,
        next_period_date_start,
        recurring_rule_type,
        recurring_interval,
        max_date_end,
        next_invoice_date=False,
        recurring_invoicing_type=False,
        recurring_invoicing_offset=False,
    ):
        """Compute the end date for the next period.

        The next period normally depends on recurrence options only.
        It is however possible to provide it a next invoice date, in
        which case this method can adjust the next period based on that
        too. In that scenario it required the invoicing type and offset
        arguments.
        """
        if not next_period_date_start:
            return False
        if max_date_end and next_period_date_start > max_date_end:
            # start is past max date end: there is no next period
            return False
        if not next_invoice_date:
            # regular algorithm
            next_period_date_end = (
                next_period_date_start
                + self.get_relative_delta(
                    recurring_rule_type, recurring_interval
                )
                - relativedelta(days=1)
            )
        else:
            # special algorithm when the next invoice date is forced
            if recurring_invoicing_type == 'pre-paid':
                next_period_date_end = (
                    next_invoice_date
                    - relativedelta(days=recurring_invoicing_offset)
                    + self.get_relative_delta(
                        recurring_rule_type, recurring_interval
                    )
                    - relativedelta(days=1)
                )
            else:  # post-paid
                next_period_date_end = (
                    next_invoice_date
                    - relativedelta(days=recurring_invoicing_offset)
                )
        if max_date_end and next_period_date_end > max_date_end:
            # end date is past max_date_end: trim it
            next_period_date_end = max_date_end
        return next_period_date_end

    @api.depends('last_date_invoiced', 'date_start', 'date_end')
    def _compute_next_period_date_start(self):
        for rec in self:
            if rec.last_date_invoiced:
                next_period_date_start = (
                    rec.last_date_invoiced + relativedelta(days=1)
                )
            else:
                next_period_date_start = rec.date_start
            if rec.date_end and next_period_date_start > rec.date_end:
                next_period_date_start = False
            rec.next_period_date_start = next_period_date_start

    @api.depends(
        'next_period_date_start',
        'recurring_invoicing_type',
        'recurring_invoicing_offset',
        'recurring_rule_type',
        'recurring_interval',
        'date_end',
        'recurring_next_date',
    )
    def _compute_next_period_date_end(self):
        for rec in self:
            rec.next_period_date_end = self.get_next_period_date_end(
                rec.next_period_date_start,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
                next_invoice_date=rec.recurring_next_date,
                recurring_invoicing_type=rec.recurring_invoicing_type,
                recurring_invoicing_offset=rec.recurring_invoicing_offset,
            )

    @api.model
    def _get_first_date_end(
        self, date_start, auto_renew_rule_type, auto_renew_interval
    ):
        return (
            date_start
            + self.get_relative_delta(
                auto_renew_rule_type, auto_renew_interval
            )
            - relativedelta(days=1)
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
                rec.date_end = self._get_first_date_end(
                    rec.date_start,
                    rec.auto_renew_rule_type,
                    rec.auto_renew_interval,
                )

    @api.onchange(
        'date_start',
        'date_end',
        'recurring_invoicing_type',
        'recurring_rule_type',
        'recurring_interval',
    )
    def _onchange_date_start(self):
        for rec in self.filtered('date_start'):
            rec.recurring_next_date = self.get_next_invoice_date(
                rec.next_period_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
            )

    @api.constrains('is_canceled', 'is_auto_renew')
    def _check_auto_renew_canceled_lines(self):
        for rec in self:
            if rec.is_canceled and rec.is_auto_renew:
                raise ValidationError(
                    _("A canceled contract line can't be set to auto-renew")
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

    @api.constrains(
        'date_start', 'date_end', 'last_date_invoiced', 'recurring_next_date'
    )
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
            if (
                rec.recurring_next_date
                and rec.recurring_next_date <= rec.last_date_invoiced
            ):
                raise ValidationError(
                    _(
                        "You can't have the next invoice date before the date "
                        "of last invoice for the contract line '%s'"
                    )
                    % rec.name
                )

    @api.constrains('recurring_next_date')
    def _check_recurring_next_date_recurring_invoices(self):
        for rec in self:
            if not rec.recurring_next_date and (
                not rec.date_end
                or not rec.last_date_invoiced
                or rec.last_date_invoiced < rec.date_end
            ):
                raise ValidationError(
                    _(
                        "You must supply a date of next invoice for contract "
                        "line '%s'"
                    )
                    % rec.name
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

    @api.depends(
        'display_type',
        'is_recurring_note',
        'recurring_next_date',
        'date_start',
        'date_end',
    )
    def _compute_create_invoice_visibility(self):
        # TODO: depending on the lines, and their order, some sections
        # have no meaning in certain invoices
        today = fields.Date.context_today(self)
        for rec in self:
            if ((not rec.display_type or rec.is_recurring_note)
                    and rec.date_start and today >= rec.date_start):
                rec.create_invoice_visibility = bool(rec.recurring_next_date)
            else:
                rec.create_invoice_visibility = False

    @api.multi
    def _prepare_invoice_line(self, invoice_id=False, invoice_values=False):
        self.ensure_one()
        dates = self._get_period_to_invoice(
            self.last_date_invoiced, self.recurring_next_date
        )
        invoice_line_vals = {
            'display_type': self.display_type,
            'product_id': self.product_id.id,
            'quantity': self._get_quantity_to_invoice(*dates),
            'uom_id': self.uom_id.id,
            'discount': self.discount,
            'contract_line_id': self.id,
        }
        if invoice_id:
            invoice_line_vals['invoice_id'] = invoice_id.id
        invoice_line = self.env['account.invoice.line'].with_context(
            force_company=self.contract_id.company_id.id,
        ).new(invoice_line_vals)
        if invoice_values and not invoice_id:
            invoice = self.env['account.invoice'].with_context(
                force_company=self.contract_id.company_id.id,
            ).new(invoice_values)
            invoice_line.invoice_id = invoice
        # Get other invoice line values from product onchange
        invoice_line._onchange_product_id()
        invoice_line_vals = invoice_line._convert_to_write(invoice_line._cache)
        # Insert markers
        name = self._insert_markers(dates[0], dates[1])
        invoice_line_vals.update(
            {
                'sequence': self.sequence,
                'name': name,
                'account_analytic_id': self.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)],
                'price_unit': self.price_unit,
            }
        )
        return invoice_line_vals

    @api.multi
    def _get_period_to_invoice(
        self, last_date_invoiced, recurring_next_date, stop_at_date_end=True
    ):
        # TODO this method can now be removed, since
        # TODO self.next_period_date_start/end have the same values
        self.ensure_one()
        if not recurring_next_date:
            return False, False, False
        first_date_invoiced = (
            last_date_invoiced + relativedelta(days=1)
            if last_date_invoiced
            else self.date_start
        )
        last_date_invoiced = self.get_next_period_date_end(
            first_date_invoiced,
            self.recurring_rule_type,
            self.recurring_interval,
            max_date_end=(self.date_end if stop_at_date_end else False),
            next_invoice_date=recurring_next_date,
            recurring_invoicing_type=self.recurring_invoicing_type,
            recurring_invoicing_offset=self.recurring_invoicing_offset,
        )
        return first_date_invoiced, last_date_invoiced, recurring_next_date

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
            last_date_invoiced = rec.next_period_date_end
            recurring_next_date = rec.get_next_invoice_date(
                last_date_invoiced + relativedelta(days=1),
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=rec.date_end,
            )
            rec.write({
                "recurring_next_date": recurring_next_date,
                "last_date_invoiced": last_date_invoiced,
            })

    @api.multi
    def _init_last_date_invoiced(self):
        """Used to init last_date_invoiced for migration purpose"""
        for rec in self:
            last_date_invoiced = rec.recurring_next_date - relativedelta(
                days=1
            )
            if rec.recurring_rule_type == 'monthlylastday':
                last_date_invoiced = (
                    rec.recurring_next_date
                    - self.get_relative_delta(
                        rec.recurring_rule_type, rec.recurring_interval - 1
                    )
                    - relativedelta(days=1)
                )
            elif rec.recurring_invoicing_type == 'post-paid':
                last_date_invoiced = (
                    rec.recurring_next_date
                    - self.get_relative_delta(
                        rec.recurring_rule_type, rec.recurring_interval
                    )
                    - relativedelta(days=1)
                )
            if last_date_invoiced > rec.date_start:
                rec.last_date_invoiced = last_date_invoiced

    @api.model
    def get_relative_delta(self, recurring_rule_type, interval):
        """Return a relativedelta for one period.

        When added to the first day of the period,
        it gives the first day of the next period.
        """
        if recurring_rule_type == 'daily':
            return relativedelta(days=interval)
        elif recurring_rule_type == 'weekly':
            return relativedelta(weeks=interval)
        elif recurring_rule_type == 'monthly':
            return relativedelta(months=interval)
        elif recurring_rule_type == 'monthlylastday':
            return relativedelta(months=interval, day=1)
        elif recurring_rule_type == 'quarterly':
            return relativedelta(months=3 * interval)
        elif recurring_rule_type == 'semesterly':
            return relativedelta(months=6 * interval)
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
            if rec.date_end:
                new_date_end = rec.date_end + delay_delta
            else:
                new_date_end = False
            new_recurring_next_date = self.get_next_invoice_date(
                new_date_start,
                rec.recurring_invoicing_type,
                rec.recurring_invoicing_offset,
                rec.recurring_rule_type,
                rec.recurring_interval,
                max_date_end=new_date_end
            )
            rec.write({
                "date_start": new_date_start,
                "date_end": new_date_end,
                "recurring_next_date": new_recurring_next_date,
            })

    @api.multi
    def _prepare_value_for_stop(self, date_end, manual_renew_needed):
        self.ensure_one()
        return {
            'date_end': date_end,
            'is_auto_renew': False,
            'manual_renew_needed': manual_renew_needed,
            'recurring_next_date': self.get_next_invoice_date(
                self.next_period_date_start,
                self.recurring_invoicing_type,
                self.recurring_invoicing_offset,
                self.recurring_rule_type,
                self.recurring_interval,
                max_date_end=date_end,
            ),
        }

    @api.multi
    def stop(self, date_end, manual_renew_needed=False, post_message=True):
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
                    old_date_end = rec.date_end
                    rec.write(
                        rec._prepare_value_for_stop(
                            date_end, manual_renew_needed
                        )
                    )
                    if post_message:
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
                else:
                    rec.write(
                        {
                            'is_auto_renew': False,
                            "manual_renew_needed": manual_renew_needed,
                        }
                    )
        return True

    @api.multi
    def _prepare_value_for_plan_successor(
        self, date_start, date_end, is_auto_renew, recurring_next_date=False
    ):
        self.ensure_one()
        if not recurring_next_date:
            recurring_next_date = self.get_next_invoice_date(
                date_start,
                self.recurring_invoicing_type,
                self.recurring_invoicing_offset,
                self.recurring_rule_type,
                self.recurring_interval,
                max_date_end=date_end,
            )
        new_vals = self.read()[0]
        new_vals.pop("id", None)
        new_vals.pop("last_date_invoiced", None)
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
        contract_line = self.env['contract.line']
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
        contract_line = self.env['contract.line']
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
                        date_start - relativedelta(days=1),
                        manual_renew_needed=True,
                        post_message=False,
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
                        date_start - relativedelta(days=1),
                        manual_renew_needed=True,
                        post_message=False,
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
        return self.write({'is_canceled': True, 'is_auto_renew': False})

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
                predecessor_contract_line = rec.predecessor_contract_line_id
                assert not predecessor_contract_line.successor_contract_line_id
                predecessor_contract_line.successor_contract_line_id = rec
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
            'res_model': 'contract.line.wizard',
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
            'res_model': 'contract.line.wizard',
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
            'name': 'Terminate contract line',
            'res_model': 'contract.line.wizard',
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
            'res_model': 'contract.line.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'target': 'new',
            'context': context,
        }

    @api.multi
    def _get_renewal_new_date_end(self):
        self.ensure_one()
        date_start = self.date_end + relativedelta(days=1)
        date_end = self._get_first_date_end(
            date_start, self.auto_renew_rule_type, self.auto_renew_interval
        )
        return date_end

    @api.multi
    def _renew_create_line(self, date_end):
        self.ensure_one()
        date_start = self.date_end + relativedelta(days=1)
        is_auto_renew = self.is_auto_renew
        self.stop(self.date_end, post_message=False)
        new_line = self.plan_successor(
            date_start, date_end, is_auto_renew, post_message=False
        )
        new_line._onchange_date_start()
        return new_line

    @api.multi
    def _renew_extend_line(self, date_end):
        self.ensure_one()
        self.date_end = date_end
        return self

    @api.multi
    def renew(self):
        res = self.env['contract.line']
        for rec in self:
            company = rec.contract_id.company_id
            date_end = rec._get_renewal_new_date_end()
            date_start = rec.date_end + relativedelta(days=1)
            if company.create_new_line_at_contract_line_renew:
                new_line = rec._renew_create_line(date_end)
            else:
                new_line = rec._renew_extend_line(date_end)
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
        return [
            ('contract_id.is_terminated', '=', False),
            ('is_auto_renew', '=', True),
            ('is_canceled', '=', False),
            ('termination_notice_date', '<=', fields.Date.context_today(self)),
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
                'contract.contract_line_supplier_tree_view'
            ).id
        if view_type == 'form':
            if default_contract_type == 'purchase':
                view_id = self.env.ref(
                    'contract.contract_line_supplier_form_view'
                ).id
            elif default_contract_type == 'sale':
                view_id = self.env.ref(
                    'contract.contract_line_customer_form_view'
                ).id
        return super().fields_view_get(
            view_id, view_type, toolbar, submenu
        )

    @api.multi
    def unlink(self):
        """stop unlink uncnacled lines"""
        for record in self:
            if not (record.is_canceled or record.display_type):
                raise ValidationError(
                    _("Contract line must be canceled before delete")
                )
        return super().unlink()

    @api.multi
    def _get_quantity_to_invoice(
        self, period_first_date, period_last_date, invoice_date
    ):
        self.ensure_one()
        return self.quantity
