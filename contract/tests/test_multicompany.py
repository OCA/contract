# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tools import mute_logger

from .test_contract import TestContractBase


class ContractMulticompanyCase(TestContractBase):
    @classmethod
    @mute_logger("odoo.addons.account.models.chart_template")
    def setUpClass(cls):
        super().setUpClass()
        cls.company_obj = cls.env["res.company"]
        cls.company_1 = cls.env.ref("base.main_company")
        vals = {"name": "Company 2"}
        cls.company_2 = cls.company_obj.create(vals)
        chart_template = cls.env["account.chart.template"]._guess_chart_template(
            cls.company_2.country_id
        )
        cls.env["account.chart.template"].try_loading(
            chart_template, company=cls.company_2, install_demo=False
        )
        cls.env.user.company_ids |= cls.company_2

        cls.contract_mc = (
            cls.env["contract.contract"]
            .with_company(cls.company_2)
            .create(
                {
                    "name": "Test Contract MC",
                    "partner_id": cls.partner.id,
                    "pricelist_id": cls.partner.property_product_pricelist.id,
                    "line_recurrence": True,
                    "contract_type": "purchase",
                }
            )
        )
        cls.line_vals = [
            {
                "contract_id": cls.contract_mc.id,
                "product_id": cls.product_1.id,
                "name": "Services from #START# to #END#",
                "quantity": 1,
                "uom_id": cls.product_1.uom_id.id,
                "price_unit": 100,
                "discount": 50,
                "recurring_rule_type": "monthly",
                "recurring_interval": 1,
                "date_start": "2018-02-15",
                "recurring_next_date": "2018-02-22",
            },
            {
                "contract_id": cls.contract_mc.id,
                "product_id": cls.product_1.id,
                "name": "Services from #START# to #END#",
                "quantity": 1,
                "uom_id": cls.product_1.uom_id.id,
                "price_unit": 100,
                "discount": 50,
                "recurring_rule_type": "monthly",
                "recurring_interval": 1,
                "date_start": "2018-01-01",
                "recurring_next_date": "2018-01-15",
            },
        ]
        cls.acct_line_mc = (
            cls.env["contract.line"].with_company(cls.company_2).create(cls.line_vals)
        )

    def test_cron_recurring_create_invoice_multi_company(self):
        today = fields.Date.context_today(self.contract2)

        self.acct_line.date_start = "2018-01-01"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.date_end = "2018-03-15"

        self.acct_line_mc[0].date_start = today - relativedelta(months=2, days=15)
        self.acct_line_mc[0].recurring_invoicing_type = "post-paid"
        self.acct_line_mc[0].date_end = today + relativedelta(months=4, days=15)

        self.acct_line_mc[1].date_start = today - relativedelta(months=3, days=15)
        self.acct_line_mc[1].recurring_invoicing_type = "post-paid"
        self.acct_line_mc[1].date_end = today + relativedelta(months=3, days=15)

        self.contract2.contract_line_ids.write(
            {
                "date_start": today - relativedelta(months=1, days=15),
                "date_end": today + relativedelta(months=11, days=15),
            }
        )

        contracts = self.contract2
        contracts_company_2 = self.env["contract.contract"].browse()
        for _i in range(10):
            contracts |= self.contract.copy()
        for _i in range(10):
            vals = (
                self.contract_mc.with_company(company=self.company_2)
                .with_context(active_test=False)
                .copy_data({"company_id": self.company_2.id})
            )
            contracts_company_2 |= self.contract_mc.with_company(
                company=self.company_2
            ).create(vals)
        self.env["contract.contract"].cron_recurring_create_invoice()
        # Check company 1
        invoice_lines_company_1 = self.env["account.move.line"].search(
            [("contract_line_id", "in", contracts.mapped("contract_line_ids").ids)]
        )
        invoice_lines_company_2 = self.env["account.move.line"].search(
            [
                (
                    "contract_line_id",
                    "in",
                    contracts_company_2.mapped("contract_line_ids").ids,
                )
            ]
        )
        self.assertEqual(
            32,  # 2 for contract2 + 3 for each contract copy (x10)
            len(invoice_lines_company_1),
        )
        self.assertEqual(
            50,  # (2 for acct_line_mc[0] + 3 for acct_line_mc[1]) x10
            len(invoice_lines_company_2),
        )
