# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import itertools
from collections import namedtuple

from odoo.fields import Date

Criteria = namedtuple(
    "Criteria",
    [
        "when",  # Contract line relatively to today (BEFORE, IN, AFTER)
        "has_date_end",  # Is date_end set on contract line (bool)
        "has_last_date_invoiced",  # Is last_date_invoiced set on contract line
        "is_auto_renew",  # Is is_auto_renew set on contract line (bool)
        "has_successor",  # Is contract line has_successor (bool)
        "predecessor_has_successor",
        # Is contract line predecessor has successor (bool)
        # In almost of the cases
        # contract_line.predecessor.successor == contract_line
        # But at cancel action,
        # contract_line.predecessor.successor == False
        # This is to permit plan_successor on predecessor
        # If contract_line.predecessor.successor != False
        # and contract_line is canceled, we don't allow uncancel
        # else we re-link contract_line and its predecessor
        "canceled",  # Is contract line canceled (bool)
    ],
)
Allowed = namedtuple(
    "Allowed", ["plan_successor", "stop_plan_successor", "stop", "cancel", "uncancel"],
)


def _expand_none(criteria):
    variations = []
    for attribute, value in criteria._asdict().items():
        if value is None:
            if attribute == "when":
                variations.append(["BEFORE", "IN", "AFTER"])
            else:
                variations.append([True, False])
        else:
            variations.append([value])
    return itertools.product(*variations)


def _add(matrix, criteria, allowed):
    """ Expand None values to True/False combination """
    for c in _expand_none(criteria):
        matrix[c] = allowed


CRITERIA_ALLOWED_DICT = {
    Criteria(
        when="BEFORE",
        has_date_end=True,
        has_last_date_invoiced=False,
        is_auto_renew=True,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="BEFORE",
        has_date_end=True,
        has_last_date_invoiced=False,
        is_auto_renew=False,
        has_successor=True,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="BEFORE",
        has_date_end=True,
        has_last_date_invoiced=False,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=True,
        stop_plan_successor=True,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="BEFORE",
        has_date_end=False,
        has_last_date_invoiced=False,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=True,
        has_last_date_invoiced=False,
        is_auto_renew=True,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=True,
        has_last_date_invoiced=False,
        is_auto_renew=False,
        has_successor=True,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=True,
        has_last_date_invoiced=False,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=True,
        stop_plan_successor=True,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=False,
        has_last_date_invoiced=False,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=True,
        uncancel=False,
    ),
    Criteria(
        when="BEFORE",
        has_date_end=True,
        has_last_date_invoiced=True,
        is_auto_renew=True,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="BEFORE",
        has_date_end=True,
        has_last_date_invoiced=True,
        is_auto_renew=False,
        has_successor=True,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="BEFORE",
        has_date_end=True,
        has_last_date_invoiced=True,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=True,
        stop_plan_successor=True,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="BEFORE",
        has_date_end=False,
        has_last_date_invoiced=True,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=True,
        has_last_date_invoiced=True,
        is_auto_renew=True,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=True,
        has_last_date_invoiced=True,
        is_auto_renew=False,
        has_successor=True,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=True,
        has_last_date_invoiced=True,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=True,
        stop_plan_successor=True,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="IN",
        has_date_end=False,
        has_last_date_invoiced=True,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=True,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="AFTER",
        has_date_end=True,
        has_last_date_invoiced=None,
        is_auto_renew=True,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="AFTER",
        has_date_end=True,
        has_last_date_invoiced=None,
        is_auto_renew=False,
        has_successor=True,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=False,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when="AFTER",
        has_date_end=True,
        has_last_date_invoiced=None,
        is_auto_renew=False,
        has_successor=False,
        predecessor_has_successor=None,
        canceled=False,
    ): Allowed(
        plan_successor=True,
        stop_plan_successor=False,
        stop=True,
        cancel=False,
        uncancel=False,
    ),
    Criteria(
        when=None,
        has_date_end=None,
        has_last_date_invoiced=None,
        is_auto_renew=None,
        has_successor=None,
        predecessor_has_successor=False,
        canceled=True,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=False,
        cancel=False,
        uncancel=True,
    ),
    Criteria(
        when=None,
        has_date_end=None,
        has_last_date_invoiced=None,
        is_auto_renew=None,
        has_successor=None,
        predecessor_has_successor=True,
        canceled=True,
    ): Allowed(
        plan_successor=False,
        stop_plan_successor=False,
        stop=False,
        cancel=False,
        uncancel=False,
    ),
}
criteria_allowed_dict = {}

for c in CRITERIA_ALLOWED_DICT:
    _add(criteria_allowed_dict, c, CRITERIA_ALLOWED_DICT[c])


def compute_when(date_start, date_end):
    today = Date.today()
    if today < date_start:
        return "BEFORE"
    if date_end and today > date_end:
        return "AFTER"
    return "IN"


def compute_criteria(
    date_start,
    date_end,
    has_last_date_invoiced,
    is_auto_renew,
    successor_contract_line_id,
    predecessor_contract_line_id,
    is_canceled,
):
    return Criteria(
        when=compute_when(date_start, date_end),
        has_date_end=bool(date_end),
        has_last_date_invoiced=bool(has_last_date_invoiced),
        is_auto_renew=is_auto_renew,
        has_successor=bool(successor_contract_line_id),
        predecessor_has_successor=bool(
            predecessor_contract_line_id.successor_contract_line_id
        ),
        canceled=is_canceled,
    )


def get_allowed(
    date_start,
    date_end,
    has_last_date_invoiced,
    is_auto_renew,
    successor_contract_line_id,
    predecessor_contract_line_id,
    is_canceled,
):
    criteria = compute_criteria(
        date_start,
        date_end,
        has_last_date_invoiced,
        is_auto_renew,
        successor_contract_line_id,
        predecessor_contract_line_id,
        is_canceled,
    )
    if criteria in criteria_allowed_dict:
        return criteria_allowed_dict[criteria]
    return False
