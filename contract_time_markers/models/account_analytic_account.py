# Copyright 2018 Road-Support - Roel Adriaans

import re

from odoo import api, fields, models
from odoo.tools.misc import format_date


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    def _format_date(self, date, partner_lang, parse):
        try:
            res = format_date(self.env, date, partner_lang, parse)
            return res
        except (AttributeError, ValueError) as e:
            # At the moment we catch exceptions silent, and return
            # an empty string.
            # Should we raise an error, or create a new mail.activity?
            return ""

    @api.model
    def _insert_markers(self, line, date_format):
        date_from = fields.Date.from_string(line.date_from)
        date_to = fields.Date.from_string(line.date_to)
        from_regex = r"#START\((.*?)\)#"
        to_regex = r"#END\((.*?)\)#"
        name = line.name

        from_result = re.findall(from_regex, name)
        to_result = re.findall(to_regex, name)

        partner_lang = line.analytic_account_id.partner_id.lang

        if from_result and len(from_result[0]) > 1:
            from_string = self._format_date(date_from, partner_lang, from_result[0])
            name = re.sub(from_regex, from_string, name)
        else:
            # Original behaviour
            name = name.replace('#START#', date_from.strftime(date_format))

        if to_result and len(to_result[0]) > 1:
            to_string = self._format_date(date_to, partner_lang, to_result[0])
            name = re.sub(to_regex, to_string, name)
        else:
            # Original behaviour
            name = name.replace('#END#', date_to.strftime(date_format))

        return name
