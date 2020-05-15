# Copyright 2018 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields
from odoo.tests.common import TransactionCase


def to_date(date):
    return fields.Date.to_date(date)


class TestProductTemplate(TransactionCase):
    def setUp(self):
        super(TestProductTemplate, self).setUp()
        self.partner = self.env.ref("base.res_partner_2")
        self.product = self.env.ref("product.product_product_1")
        self.contract = self.env["contract.contract"].create(
            {
                "name": "Test Contract 2",
                "partner_id": self.partner.id,
                "pricelist_id": self.partner.property_product_pricelist.id,
                "contract_type": "purchase",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.product.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": self.product.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2016-02-15",
                            "recurring_next_date": "2016-02-29",
                        },
                    )
                ],
            }
        )
        self.contract_line = self.contract.contract_line_ids[0]

    def test_compute_prorated(self):
        def update_contract_line(
            case,
            recurring_rule_type,
            recurring_interval,
            recurring_invoicing_type,
            date_start,
            recurring_next_date,
            date_end,
            last_date_invoiced=False,
        ):
            self.contract_line.write(
                {
                    "recurring_rule_type": recurring_rule_type,
                    "recurring_invoicing_type": recurring_invoicing_type,
                    "recurring_interval": recurring_interval,
                    "date_start": date_start,
                    "recurring_next_date": recurring_next_date,
                    "date_end": date_end,
                    "last_date_invoiced": last_date_invoiced,
                }
            )

        def error_message(
            case,
            recurring_rule_type,
            recurring_interval,
            recurring_invoicing_type,
            date_start,
            recurring_next_date,
            date_end,
            last_date_invoiced=False,
        ):
            return (
                "%s : Error in %s every %d %s case, start %s, next %s, end %s,"
                " last %s"
                % (
                    case,
                    recurring_invoicing_type,
                    recurring_interval,
                    recurring_rule_type,
                    date_start,
                    recurring_next_date,
                    date_end,
                    last_date_invoiced or "",
                )
            )

        combinations = [
            (
                1.00,
                (
                    "Case 1",
                    "monthly",
                    1,
                    "pre-paid",
                    to_date("2018-01-05"),
                    to_date("2018-01-05"),
                    False,
                ),
            ),
            (
                1.00,
                (
                    "Case 2",
                    "monthly",
                    1,
                    "pre-paid",
                    to_date("2018-01-05"),
                    to_date("2018-02-01"),
                    False,
                    to_date("2018-01-31"),
                ),
            ),
            (
                1.00,
                (
                    "Case 3",
                    "monthly",
                    1,
                    "pre-paid",
                    to_date("2017-01-05"),
                    to_date("2018-02-01"),
                    to_date("2018-03-01"),
                    to_date("2018-01-31"),
                ),
            ),
            (
                0.892,
                (
                    "Case 4",
                    "monthly",
                    1,
                    "pre-paid",
                    to_date("2017-01-05"),
                    to_date("2018-02-01"),
                    to_date("2018-02-25"),
                    to_date("2018-01-31"),
                ),
            ),
            (
                1.00,
                (
                    "Case 5",
                    "monthly",
                    1,
                    "post-paid",
                    to_date("2018-01-05"),
                    to_date("2018-02-05"),
                    False,
                ),
            ),
            (
                0.87,
                (
                    "Case 6",
                    "monthly",
                    1,
                    "post-paid",
                    to_date("2018-01-05"),
                    to_date("2018-02-01"),
                    False,
                ),
            ),
            (
                1.00,
                (
                    "Case 7",
                    "monthly",
                    1,
                    "post-paid",
                    to_date("2017-01-05"),
                    to_date("2018-02-01"),
                    to_date("2018-03-01"),
                    to_date("2017-12-31"),
                ),
            ),
            (
                0.892,
                (
                    "Case 8",
                    "monthly",
                    1,
                    "post-paid",
                    to_date("2017-01-05"),
                    to_date("2018-03-01"),
                    to_date("2018-02-25"),
                    to_date("2018-01-31"),
                ),
            ),
            (
                1.00,
                (
                    "Case 9",
                    "monthlylastday",
                    1,
                    "post-paid",
                    to_date("2018-01-01"),
                    to_date("2018-01-31"),
                    to_date("2018-02-25"),
                ),
            ),
            (
                0.87,
                (
                    "Case 10",
                    "monthlylastday",
                    1,
                    "post-paid",
                    to_date("2018-01-05"),
                    to_date("2018-01-31"),
                    to_date("2018-02-25"),
                ),
            ),
            (
                0.892,
                (
                    "Case 11",
                    "monthlylastday",
                    1,
                    "post-paid",
                    to_date("2018-01-05"),
                    to_date("2018-02-28"),
                    to_date("2018-02-25"),
                    to_date("2018-01-31"),
                ),
            ),
            (
                0.5,
                (
                    "Case 12",
                    "monthlylastday",
                    1,
                    "post-paid",
                    to_date("2018-02-01"),
                    to_date("2018-02-28"),
                    to_date("2018-02-14"),
                ),
            ),
            (
                0.5,
                (
                    "Case 13",
                    "monthlylastday",
                    1,
                    "post-paid",
                    to_date("2018-02-15"),
                    to_date("2018-02-28"),
                    False,
                ),
            ),
            (
                0.032,
                (
                    "Case 14",
                    "monthlylastday",
                    1,
                    "post-paid",
                    to_date("2017-02-15"),
                    to_date("2018-01-31"),
                    False,
                    to_date("2018-01-30"),
                ),
            ),
            (
                1.035,
                (
                    "Case 15",
                    "monthlylastday",
                    1,
                    "post-paid",
                    to_date("2017-02-15"),
                    to_date("2018-02-28"),
                    False,
                    to_date("2018-01-30"),
                ),
            ),
            (
                0.032,
                (
                    "Case 16",
                    "monthly",
                    1,
                    "post-paid",
                    to_date("2017-02-15"),
                    to_date("2018-02-01"),
                    False,
                    to_date("2018-01-30"),
                ),
            ),
            (
                1.035,
                (
                    "Case 17",
                    "monthly",
                    1,
                    "post-paid",
                    to_date("2017-02-15"),
                    to_date("2018-03-01"),
                    False,
                    to_date("2018-01-30"),
                ),
            ),
            (
                1.0,
                (
                    "Case 18",
                    "monthly",
                    1,
                    "pre-paid",
                    to_date("2017-02-15"),
                    to_date("2018-01-01"),
                    False,
                    to_date("2017-12-31"),
                ),
            ),
            (
                1.035,
                (
                    "Case 19",
                    "monthly",
                    1,
                    "pre-paid",
                    to_date("2017-02-15"),
                    to_date("2018-02-01"),
                    False,
                    to_date("2018-01-30"),
                ),
            ),
            (
                1.566,
                (
                    "Case 19",
                    "monthlylastday",
                    1,
                    "pre-paid",
                    to_date("2018-03-15"),
                    to_date("2018-04-30"),
                    False,
                ),
            ),
            (
                1.48,
                (
                    "Case 20",
                    "monthly",
                    1,
                    "post-paid",
                    to_date("2018-03-15"),
                    to_date("2018-04-30"),
                    False,
                ),
            ),
            (
                2.53,
                (
                    "Case 21",
                    "monthly",
                    1,
                    "pre-paid",
                    to_date("2018-03-15"),
                    to_date("2018-04-30"),
                    False,
                ),
            ),
            (
                1,
                (
                    "Case 22",
                    "monthlylastday",
                    1,
                    "pre-paid",
                    to_date("2018-03-01"),
                    to_date("2018-03-01"),
                    False,
                ),
            ),
            (
                0.5,
                (
                    "Case 23",
                    "monthlylastday",
                    1,
                    "pre-paid",
                    to_date("2018-04-16"),
                    to_date("2018-04-16"),
                    False,
                ),
            ),
        ]
        for result, combination in combinations:
            update_contract_line(*combination)
            dates = self.contract_line._get_period_to_invoice(
                self.contract_line.last_date_invoiced,
                self.contract_line.recurring_next_date,
            )
            self.assertAlmostEqual(
                result,
                self.contract_line.compute_prorated(*dates),
                places=2,
                msg=error_message(*combination),
            )
