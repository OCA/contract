# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from collections import namedtuple
from odoo.fields import Date

CRITERIA = namedtuple(
    'CRITERIA',
    [
        'WHEN',
        'HAS_DATE_END',
        'IS_AUTO_RENEW',
        'HAS_SUCCESSOR',
        'PREDECESSOR_HAS_SUCCESSOR',
        'CANCELED',
    ],
)
ALLOWED = namedtuple(
    'ALLOWED',
    ['PLAN_SUCCESSOR', 'STOP_PLAN_SUCCESSOR', 'STOP', 'CANCEL', 'UN_CANCEL'],
)

CRITERIA_ALLOWED_DICT = {
    CRITERIA(
        WHEN='BEFORE',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=True,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=True,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='BEFORE',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=True,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=False,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='BEFORE',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=True,
        STOP_PLAN_SUCCESSOR=True,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='BEFORE',
        HAS_DATE_END=False,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=True,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='IN',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=True,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=True,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='IN',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=True,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=False,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='IN',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=True,
        STOP_PLAN_SUCCESSOR=True,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='IN',
        HAS_DATE_END=False,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=True,
        STOP=True,
        CANCEL=True,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='AFTER',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=True,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=False,
        STOP=False,
        CANCEL=False,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='AFTER',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=True,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=False,
        STOP=False,
        CANCEL=False,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN='AFTER',
        HAS_DATE_END=True,
        IS_AUTO_RENEW=False,
        HAS_SUCCESSOR=False,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=False,
    ): ALLOWED(
        PLAN_SUCCESSOR=True,
        STOP_PLAN_SUCCESSOR=False,
        STOP=False,
        CANCEL=False,
        UN_CANCEL=False,
    ),
    CRITERIA(
        WHEN=None,
        HAS_DATE_END=None,
        IS_AUTO_RENEW=None,
        HAS_SUCCESSOR=None,
        PREDECESSOR_HAS_SUCCESSOR=False,
        CANCELED=True,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=False,
        STOP=False,
        CANCEL=False,
        UN_CANCEL=True,
    ),
    CRITERIA(
        WHEN=None,
        HAS_DATE_END=None,
        IS_AUTO_RENEW=None,
        HAS_SUCCESSOR=None,
        PREDECESSOR_HAS_SUCCESSOR=True,
        CANCELED=True,
    ): ALLOWED(
        PLAN_SUCCESSOR=False,
        STOP_PLAN_SUCCESSOR=False,
        STOP=False,
        CANCEL=False,
        UN_CANCEL=False,
    ),
}


def compute_when(date_start, date_end):
    today = Date.today()
    if today < date_start:
        return 'BEFORE'
    if date_end and today > date_end:
        return 'AFTER'
    return 'IN'


def compute_criteria(
    date_start,
    date_end,
    is_auto_renew,
    successor_contract_line_id,
    predecessor_contract_line_id,
    is_canceled,
):
    if is_canceled:
        if (
            not predecessor_contract_line_id
            or not predecessor_contract_line_id.successor_contract_line_id
        ):
            return CRITERIA(
                WHEN=None,
                HAS_DATE_END=None,
                IS_AUTO_RENEW=None,
                HAS_SUCCESSOR=None,
                PREDECESSOR_HAS_SUCCESSOR=False,
                CANCELED=True,
            )
        else:
            return CRITERIA(
                WHEN=None,
                HAS_DATE_END=None,
                IS_AUTO_RENEW=None,
                HAS_SUCCESSOR=None,
                PREDECESSOR_HAS_SUCCESSOR=True,
                CANCELED=True,
            )
    when = compute_when(date_start, date_end)
    has_date_end = date_end if not date_end else True
    is_auto_renew = is_auto_renew
    has_successor = True if successor_contract_line_id else False
    canceled = is_canceled
    return CRITERIA(
        WHEN=when,
        HAS_DATE_END=has_date_end,
        IS_AUTO_RENEW=is_auto_renew,
        HAS_SUCCESSOR=has_successor,
        PREDECESSOR_HAS_SUCCESSOR=None,
        CANCELED=canceled,
    )


def get_allowed(
    date_start,
    date_end,
    is_auto_renew,
    successor_contract_line_id,
    predecessor_contract_line_id,
    is_canceled,
):
    criteria = compute_criteria(
        date_start,
        date_end,
        is_auto_renew,
        successor_contract_line_id,
        predecessor_contract_line_id,
        is_canceled,
    )
    if criteria in CRITERIA_ALLOWED_DICT:
        return CRITERIA_ALLOWED_DICT[criteria]
    return False
