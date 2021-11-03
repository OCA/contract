# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .test_contract import TestContractBase


class ContractMulticompanyCase(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chart_template = cls.env.ref("l10n_generic_coa.configurable_chart_template")
        cls.company_obj = cls.env["res.company"]
        cls.company_1 = cls.env.ref("base.main_company")
        vals = {"name": "Company 2"}
        cls.company_2 = cls.company_obj.create(vals)
        chart_template.try_loading(company=cls.company_2)
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
                    "contract_line_ids": [
                        (
                            0,
                            0,
                            {
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
                        )
                    ],
                }
            )
        )
        cls.line_vals = {
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
            "is_auto_renew": False,
        }
        cls.acct_line_mc = (
            cls.env["contract.line"].with_company(cls.company_2).create(cls.line_vals)
        )

    def test_cron_recurring_create_invoice_multi_company(self):
        self.acct_line.date_start = "2018-01-01"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.date_end = "2018-03-15"

        self.acct_line_mc.date_start = "2018-01-01"
        self.acct_line_mc.recurring_invoicing_type = "post-paid"
        self.acct_line_mc.date_end = "2018-03-15"

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
            len(contracts.mapped("contract_line_ids")), len(invoice_lines_company_1)
        )
        self.assertEqual(
            len(contracts_company_2.mapped("contract_line_ids")),
            len(invoice_lines_company_2),
        )
