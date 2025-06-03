# Copyright 2018 Tecnativa - Carlos Dauden
# Copyright 2018-2020 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from collections import namedtuple

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import Command, fields
from odoo.exceptions import ValidationError
from odoo.tests import Form, common


def to_date(date):
    return fields.Date.to_date(date)


class TestContractBase(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "pricelist for contract test"}
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "partner test contract",
                "property_product_pricelist": cls.pricelist.id,
                "email": "demo@demo.com",
            }
        )
        cls.product_1 = cls.env.ref("product.product_product_1")
        cls.product_2 = cls.env.ref("product.product_product_2")
        cls.product_1.taxes_id += cls.env["account.tax"].search(
            [("type_tax_use", "=", "sale")], limit=1
        )
        cls.product_1.description_sale = "Test description sale"
        cls.line_template_vals = {
            "product_id": cls.product_1.id,
            "name": "Services from #START# to #END#",
            "quantity": 1,
            "uom_id": cls.product_1.uom_id.id,
            "price_unit": 100,
            "discount": 50,
            "recurring_rule_type": "yearly",
            "recurring_interval": 1,
        }
        cls.section_template_vals = {
            "display_type": "line_section",
            "name": "Test section",
        }
        cls.template_vals = {
            "name": "Test Contract Template",
            "contract_line_ids": [
                Command.create(cls.section_template_vals),
                Command.create(cls.line_template_vals),
            ],
        }
        cls.template = cls.env["contract.template"].create(cls.template_vals)
        # For being sure of the applied price
        cls.env["product.pricelist.item"].create(
            {
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "product_id": cls.product_1.id,
                "compute_price": "formula",
                "base": "list_price",
            }
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": True,
            }
        )
        cls.contract2 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 2",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": True,
                "contract_type": "purchase",
                "contract_line_ids": [
                    Command.create(
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
        cls.line_vals = {
            "contract_id": cls.contract.id,
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
        }
        cls.acct_line = cls.env["contract.line"].create(cls.line_vals)
        cls.contract3 = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 3",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.partner.property_product_pricelist.id,
                "line_recurrence": False,
                "contract_type": "sale",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2018-02-15",
                "contract_line_ids": [
                    Command.create(
                        {
                            "product_id": False,
                            "name": "Header for #INVOICEMONTHNAME# Services",
                            "display_type": "line_section",
                        },
                    ),
                    Command.create(
                        {
                            "product_id": False,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "price_unit": 100,
                        },
                    ),
                    Command.create(
                        {
                            "product_id": False,
                            "name": "Line",
                            "quantity": 1,
                            "price_unit": 120,
                        },
                    ),
                ],
            }
        )


class TestContract(TestContractBase):
    def _add_template_line(self, overrides=None):
        if overrides is None:
            overrides = {}
        vals = self.line_vals.copy()
        del vals["contract_id"]
        del vals["date_start"]
        vals["contract_id"] = self.template.id
        vals.update(overrides)
        return self.env["contract.template.line"].create(vals)

    def _get_mail_messages_prev(self, contract, subtype):
        return (
            self.env["mail.message"]
            .search(
                [
                    ("model", "=", "contract.contract"),
                    ("res_id", "=", contract.id),
                    ("subtype_id", "=", subtype.id),
                ]
            )
            .ids
        )

    def _get_mail_messages(self, exclude_ids, contract, subtype):
        return self.env["mail.message"].search(
            [
                ("model", "=", "contract.contract"),
                ("res_id", "=", contract.id),
                ("subtype_id", "=", subtype.id),
                ("id", "not in", exclude_ids),
            ]
        )

    def test_add_modifications(self):
        partner2 = self.partner.copy()
        self.contract.message_subscribe(
            partner_ids=partner2.ids, subtype_ids=self.env.ref("mail.mt_comment").ids
        )
        subtype = self.env.ref("contract.mail_message_subtype_contract_modification")
        partner_ids = self.contract.message_follower_ids.filtered(
            lambda x: subtype in x.subtype_ids
        ).mapped("partner_id")
        self.assertGreaterEqual(len(partner_ids), 1)
        # Check initial modification auto-creation
        self.assertEqual(len(self.contract.modification_ids), 1)
        exclude_ids = self._get_mail_messages_prev(self.contract, subtype)
        self.contract.write(
            {
                "modification_ids": [
                    Command.create(
                        {"date": "2020-01-01", "description": "Modification 1"}
                    ),
                    Command.create(
                        {"date": "2020-02-01", "description": "Modification 2"}
                    ),
                ]
            }
        )
        mail_messages = self._get_mail_messages(exclude_ids, self.contract, subtype)
        self.assertGreaterEqual(len(mail_messages), 1)
        self.assertEqual(
            mail_messages[0].notification_ids.mapped("res_partner_id").ids,
            self.contract.partner_id.ids,
        )

    def test_check_discount(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write({"discount": 120})

    def test_automatic_price(self):
        self.acct_line.automatic_price = True
        self.product_1.list_price = 1100
        self.assertEqual(self.acct_line.price_unit, 1100)
        # Try to write other price
        self.acct_line.price_unit = 10
        self.acct_line.invalidate_model()
        self.assertEqual(self.acct_line.price_unit, 1100)
        # Now disable automatic price
        self.acct_line.automatic_price = False
        self.acct_line.price_unit = 10
        self.acct_line.invalidate_model()
        self.assertEqual(self.acct_line.price_unit, 10)

    def test_automatic_price_change(self):
        self.acct_line.automatic_price = True
        self.product_1.list_price = 1100
        self.assertEqual(self.acct_line.price_unit, 1100)
        # Change contract type
        self.acct_line.contract_id.contract_type = "purchase"
        self.assertFalse(self.acct_line.automatic_price)

    def test_contract(self):
        self.assertEqual(self.contract.recurring_next_date, to_date("2018-01-15"))
        self.assertAlmostEqual(self.acct_line.price_subtotal, 50.0)
        self.acct_line.price_unit = 100.0
        self.contract.partner_id = self.partner.id
        self.contract.recurring_create_invoice()
        self.invoice_monthly = self.contract._get_related_invoices()
        self.assertTrue(self.invoice_monthly)
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-02-15"))
        self.inv_line = self.invoice_monthly.invoice_line_ids[0]
        self.assertTrue(self.inv_line.tax_ids)
        self.assertAlmostEqual(self.inv_line.price_subtotal, 50.0)
        self.assertEqual(self.contract.user_id, self.invoice_monthly.user_id)

    def test_contract_level_recurrence(self):
        self.contract3.recurring_create_invoice()
        self.contract3.flush_recordset()

    def test_contract_daily(self):
        recurring_next_date = to_date("2018-02-23")
        last_date_invoiced = to_date("2018-02-22")
        self.acct_line.recurring_rule_type = "daily"
        self.contract.pricelist_id = False
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoice_daily = self.contract._get_related_invoices()
        self.assertTrue(invoice_daily)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_invoice_followers(self):
        self.acct_line.recurring_next_date = "2018-02-23"
        self.acct_line.recurring_rule_type = "daily"
        self.contract.pricelist_id = False
        subtype_ids = self.contract.message_follower_ids.filtered(
            lambda x: self.contract.partner_id.id == x.partner_id.id
        ).subtype_ids.ids
        subtype_ids.append(
            self.env.ref("contract.mail_message_subtype_invoice_created").id
        )
        self.contract.message_subscribe(
            partner_ids=self.contract.partner_id.ids, subtype_ids=subtype_ids
        )
        self.contract._recurring_create_invoice()
        invoice_daily = self.contract._get_related_invoices()
        self.assertTrue(invoice_daily)
        self.assertTrue(self.contract.partner_id in invoice_daily.message_partner_ids)

    def test_contract_invoice_salesperson(self):
        self.acct_line.recurring_next_date = "2018-02-23"
        self.acct_line.recurring_rule_type = "daily"
        new_salesperson = self.env["res.users"].create(
            {"name": "Some Salesperson", "login": "salesperson_test"}
        )
        self.contract.user_id = new_salesperson
        self.contract._recurring_create_invoice()
        invoice_daily = self.contract._get_related_invoices()
        self.assertTrue(invoice_daily)
        self.assertEqual(self.contract.user_id, invoice_daily.user_id)
        self.assertEqual(self.contract.user_id, invoice_daily.invoice_user_id)

    def test_contract_weekly_post_paid(self):
        recurring_next_date = to_date("2018-03-01")
        last_date_invoiced = to_date("2018-02-21")
        self.acct_line.recurring_rule_type = "weekly"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_weekly_pre_paid(self):
        recurring_next_date = to_date("2018-03-01")
        last_date_invoiced = to_date("2018-02-28")
        self.acct_line.recurring_rule_type = "weekly"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_yearly_post_paid(self):
        recurring_next_date = to_date("2019-02-22")
        last_date_invoiced = to_date("2018-02-21")
        self.acct_line.recurring_rule_type = "yearly"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_yearly_pre_paid(self):
        recurring_next_date = to_date("2019-02-22")
        last_date_invoiced = to_date("2019-02-21")
        self.acct_line.date_end = "2020-02-22"
        self.acct_line.recurring_rule_type = "yearly"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_monthly_lastday(self):
        recurring_next_date = to_date("2018-02-28")
        last_date_invoiced = to_date("2018-02-22")
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_rule_type = "monthlylastday"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_monthly_lastday = self.contract._get_related_invoices()
        self.assertTrue(invoices_monthly_lastday)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_quarterly_pre_paid(self):
        recurring_next_date = to_date("2018-05-22")
        last_date_invoiced = to_date("2018-05-21")
        self.acct_line.date_end = "2020-02-22"
        self.acct_line.recurring_rule_type = "quarterly"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_quarterly_post_paid(self):
        recurring_next_date = to_date("2018-05-22")
        last_date_invoiced = to_date("2018-02-21")
        self.acct_line.date_end = "2020-02-22"
        self.acct_line.recurring_rule_type = "quarterly"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_semesterly_pre_paid(self):
        recurring_next_date = to_date("2018-08-22")
        last_date_invoiced = to_date("2018-08-21")
        self.acct_line.date_end = "2020-02-22"
        self.acct_line.recurring_rule_type = "semesterly"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_contract_semesterly_post_paid(self):
        recurring_next_date = to_date("2018-08-22")
        last_date_invoiced = to_date("2018-02-21")
        self.acct_line.date_end = "2020-02-22"
        self.acct_line.recurring_rule_type = "semesterly"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_next_date = "2018-02-22"
        self.contract.recurring_create_invoice()
        invoices_weekly = self.contract._get_related_invoices()
        self.assertTrue(invoices_weekly)
        self.assertEqual(self.acct_line.recurring_next_date, recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, last_date_invoiced)

    def test_last_invoice_post_paid(self):
        self.acct_line.date_start = "2018-01-01"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.date_end = "2018-03-15"
        self.assertTrue(self.acct_line.create_invoice_visibility)
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-02-01"))
        self.assertFalse(self.acct_line.last_date_invoiced)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-03-01"))
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-01-31"))
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-3-16"))
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-03-15"))
        self.assertFalse(self.acct_line.recurring_next_date)
        self.assertFalse(self.acct_line.create_invoice_visibility)
        invoices = self.contract._get_related_invoices()
        self.contract.recurring_create_invoice()
        new_invoices = self.contract._get_related_invoices()
        self.assertEqual(
            invoices,
            new_invoices,
            "Should not create a new invoice after the last one",
        )

    def test_last_invoice_pre_paid(self):
        self.acct_line.date_start = "2018-01-01"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.date_end = "2018-03-15"
        self.assertTrue(self.acct_line.create_invoice_visibility)
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-01-01"))
        self.assertFalse(self.acct_line.last_date_invoiced)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-02-01"))
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-01-31"))
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-03-15"))
        self.assertFalse(self.acct_line.recurring_next_date)
        self.assertFalse(self.acct_line.create_invoice_visibility)
        invoices = self.contract._get_related_invoices()
        self.contract.recurring_create_invoice()
        new_invoices = self.contract._get_related_invoices()
        self.assertEqual(
            invoices,
            new_invoices,
            "Should not create a new invoice after the last one",
        )

    def test_onchange_partner_id(self):
        self.contract._onchange_partner_id()
        self.assertEqual(
            self.contract.pricelist_id,
            self.contract.partner_id.property_product_pricelist,
        )

    def test_uom(self):
        uom_litre = self.env.ref("uom.product_uom_litre")
        self.acct_line.uom_id = uom_litre.id
        product = self.acct_line.product_id
        self.acct_line.product_id = False
        self.acct_line.product_id = product
        self.assertEqual(self.acct_line.uom_id, self.acct_line.product_id.uom_id)

    def test_no_pricelist(self):
        self.contract.pricelist_id = False
        self.acct_line.quantity = 2
        self.assertAlmostEqual(self.acct_line.price_subtotal, 100.0)

    def test_check_journal(self):
        journal = self.env["account.journal"].search([("type", "=", "sale")])
        journal.write({"type": "general"})
        with self.assertRaises(ValidationError):
            self.contract.recurring_create_invoice()

    def test_check_date_end(self):
        with self.assertRaises(ValidationError):
            self.acct_line.date_end = "2015-12-31"

    def test_check_recurring_next_date_start_date(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {"date_start": "2018-01-01", "recurring_next_date": "2017-01-01"}
            )

    def test_onchange_contract_template_id(self):
        """It should change the contract values to match the template."""
        self.contract.contract_template_id = False
        self.contract._onchange_contract_template_id()
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        res = {
            "contract_line_ids": [
                Command.create(
                    {"display_type": "line_section", "name": "Test section"}
                ),
                Command.create(
                    {
                        "product_id": self.product_1.id,
                        "name": "Services from #START# to #END#",
                        "quantity": 1,
                        "uom_id": self.product_1.uom_id.id,
                        "price_unit": 100,
                        "discount": 50,
                        "recurring_rule_type": "yearly",
                        "recurring_interval": 1,
                    },
                ),
            ]
        }
        del self.template_vals["name"]
        self.assertDictEqual(res, self.template_vals)

    def test_onchange_contract_template_id_lines(self):
        """It should create invoice lines for the contract lines."""
        self.acct_line.unlink()
        self.contract.contract_template_id = self.template

        self.assertFalse(
            self.contract.contract_line_ids,
            "Recurring lines were not removed.",
        )
        self.contract.contract_template_id = self.template
        self.contract._onchange_contract_template_id()
        self.assertEqual(len(self.contract.contract_line_ids), 2)
        for index, vals in [
            (0, self.section_template_vals),
            (1, self.line_template_vals),
        ]:
            contract_line = self.contract.contract_line_ids[index]
            for key, value in vals.items():
                test_value = contract_line[key]
                try:
                    test_value = test_value.id
                except AttributeError as ae:
                    # This try/except is for relation fields.
                    # For normal fields, test_value would be
                    # str, float, int ... without id
                    logging.info(
                        "Ignored AttributeError ('%s' is not a relation field): %s",
                        key,
                        ae,
                    )
                self.assertEqual(test_value, value)

    def test_send_mail_contract(self):
        result = self.contract.action_contract_send()
        self.assertEqual(result["res_model"], "mail.compose.message")

    def test_contract_onchange_product_id_name(self):
        """It should update the name for the line."""
        line = self._add_template_line()
        self.product_2.description_sale = "Test Name Change"
        line.product_id = self.product_2
        self.assertEqual(
            line.name, line.product_id.get_product_multiline_description_sale()
        )

    def test_contract_count(self):
        """It should return sale contract count."""
        sale_count = self.partner.sale_contract_count + 2
        self.contract.copy()
        self.contract.copy()
        purchase_count = self.partner.purchase_contract_count + 1
        self.contract2.copy()
        self.partner.invalidate_model()
        self.assertEqual(self.partner.sale_contract_count, sale_count)
        self.assertEqual(self.partner.purchase_contract_count, purchase_count)

    def test_same_date_start_and_date_end(self):
        """It should create one invoice with same start and end date."""
        self.acct_line.write(
            {
                "date_start": self.today,
                "date_end": self.today,
                "recurring_next_date": self.today,
            }
        )
        self.contract._compute_recurring_next_date()
        init_count = len(self.contract._get_related_invoices())
        self.contract.recurring_create_invoice()
        last_count = len(self.contract._get_related_invoices())
        self.assertEqual(last_count, init_count + 1)
        self.contract.recurring_create_invoice()
        last_count = len(self.contract._get_related_invoices())
        self.assertEqual(last_count, init_count + 1)

    def test_act_show_contract(self):
        show_contract = self.partner.with_context(
            contract_type="sale"
        ).act_show_contract()
        self.assertEqual(
            show_contract,
            {
                **show_contract,
                **{
                    "name": "Customer Contracts",
                    "type": "ir.actions.act_window",
                    "res_model": "contract.contract",
                    "xml_id": "contract.action_customer_contract",
                },
            },
            "There was an error and the view couldn't be opened.",
        )

    def test_get_default_recurring_invoicing_offset(self):
        clm = self.env["contract.line"]
        self.assertEqual(
            clm._get_default_recurring_invoicing_offset("pre-paid", "monthly"), 0
        )
        self.assertEqual(
            clm._get_default_recurring_invoicing_offset("post-paid", "monthly"), 1
        )
        self.assertEqual(
            clm._get_default_recurring_invoicing_offset("pre-paid", "monthlylastday"), 0
        )
        self.assertEqual(
            clm._get_default_recurring_invoicing_offset("post-paid", "monthlylastday"),
            0,
        )

    def test_get_next_invoice_date(self):
        """Test different combination to compute recurring_next_date
        Combination format
        {
            'recurring_next_date': (      # date
                date_start,               # date
                recurring_invoicing_type, # ('pre-paid','post-paid',)
                recurring_rule_type,      # ('daily', 'weekly', 'monthly',
                                          #  'monthlylastday', 'yearly'),
                recurring_interval,       # integer
                max_date_end,             # date
            ),
        }
        """

        def error_message(
            date_start,
            recurring_invoicing_type,
            recurring_invoicing_offset,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
        ):
            return (
                "Error in %s-%d every %d %s case, "
                "start with %s (max_date_end=%s)"
                % (
                    recurring_invoicing_type,
                    recurring_invoicing_offset,
                    recurring_interval,
                    recurring_rule_type,
                    date_start,
                    max_date_end,
                )
            )

        combinations = [
            (
                to_date("2018-01-01"),
                (to_date("2018-01-01"), "pre-paid", 0, "monthly", 1, False),
            ),
            (
                to_date("2018-01-01"),
                (
                    to_date("2018-01-01"),
                    "pre-paid",
                    0,
                    "monthly",
                    1,
                    to_date("2018-01-15"),
                ),
            ),
            (
                False,
                (
                    to_date("2018-01-16"),
                    "pre-paid",
                    0,
                    "monthly",
                    1,
                    to_date("2018-01-15"),
                ),
            ),
            (
                to_date("2018-01-01"),
                (to_date("2018-01-01"), "pre-paid", 0, "monthly", 2, False),
            ),
            (
                to_date("2018-02-01"),
                (to_date("2018-01-01"), "post-paid", 1, "monthly", 1, False),
            ),
            (
                to_date("2018-01-16"),
                (
                    to_date("2018-01-01"),
                    "post-paid",
                    1,
                    "monthly",
                    1,
                    to_date("2018-01-15"),
                ),
            ),
            (
                False,
                (
                    to_date("2018-01-16"),
                    "post-paid",
                    1,
                    "monthly",
                    1,
                    to_date("2018-01-15"),
                ),
            ),
            (
                to_date("2018-03-01"),
                (to_date("2018-01-01"), "post-paid", 1, "monthly", 2, False),
            ),
            (
                to_date("2018-01-31"),
                (to_date("2018-01-05"), "post-paid", 0, "monthlylastday", 1, False),
            ),
            (
                to_date("2018-01-06"),
                (to_date("2018-01-06"), "pre-paid", 0, "monthlylastday", 1, False),
            ),
            (
                to_date("2018-02-28"),
                (to_date("2018-01-05"), "post-paid", 0, "monthlylastday", 2, False),
            ),
            (
                to_date("2018-01-05"),
                (to_date("2018-01-05"), "pre-paid", 0, "monthlylastday", 2, False),
            ),
            (
                to_date("2018-01-05"),
                (to_date("2018-01-05"), "pre-paid", 0, "yearly", 1, False),
            ),
            (
                to_date("2019-01-05"),
                (to_date("2018-01-05"), "post-paid", 1, "yearly", 1, False),
            ),
        ]
        contract_line_env = self.env["contract.line"]
        for recurring_next_date, combination in combinations:
            self.assertEqual(
                recurring_next_date,
                contract_line_env.get_next_invoice_date(*combination),
                error_message(*combination),
            )

    def test_next_invoicing_period(self):
        """Test different combination for next invoicing period
        {
            (
                'recurring_next_date',    # date
                'next_period_date_start', # date
                'next_period_date_end'    # date
                ): (
                date_start,               # date
                date_end,                 # date
                last_date_invoiced,       # date
                recurring_next_date,      # date
                recurring_invoicing_type, # ('pre-paid','post-paid',)
                recurring_rule_type,      # ('daily', 'weekly', 'monthly',
                                          #  'monthlylastday', 'yearly'),
                recurring_interval,       # integer
                max_date_end,             # date
            ),
        }
        """

        def _update_contract_line(
            case,
            date_start,
            date_end,
            last_date_invoiced,
            recurring_next_date,
            recurring_invoicing_type,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
        ):
            self.acct_line.write(
                {
                    "date_start": date_start,
                    "date_end": date_end,
                    "last_date_invoiced": last_date_invoiced,
                    "recurring_next_date": recurring_next_date,
                    "recurring_invoicing_type": recurring_invoicing_type,
                    "recurring_rule_type": recurring_rule_type,
                    "recurring_interval": recurring_interval,
                }
            )

        def _get_result():
            return Result(
                recurring_next_date=self.acct_line.recurring_next_date,
                next_period_date_start=self.acct_line.next_period_date_start,
                next_period_date_end=self.acct_line.next_period_date_end,
            )

        def _error_message(
            case,
            date_start,
            date_end,
            last_date_invoiced,
            recurring_next_date,
            recurring_invoicing_type,
            recurring_rule_type,
            recurring_interval,
            max_date_end,
        ):
            return (
                f"Error in case {case}:"
                f"date_start: {date_start}, "
                f"date_end: {date_end}, "
                f"last_date_invoiced: {last_date_invoiced}, "
                f"recurring_next_date: {recurring_next_date}, "
                f"recurring_invoicing_type: {recurring_invoicing_type}, "
                f"recurring_rule_type: {recurring_rule_type}, "
                f"recurring_interval: {recurring_interval}, "
                f"max_date_end: {max_date_end}, "
            )

        Result = namedtuple(
            "Result",
            ["recurring_next_date", "next_period_date_start", "next_period_date_end"],
        )
        Combination = namedtuple(
            "Combination",
            [
                "case",
                "date_start",
                "date_end",
                "last_date_invoiced",
                "recurring_next_date",
                "recurring_invoicing_type",
                "recurring_rule_type",
                "recurring_interval",
                "max_date_end",
            ],
        )
        combinations = {
            Result(
                recurring_next_date=to_date("2019-01-01"),
                next_period_date_start=to_date("2019-01-01"),
                next_period_date_end=to_date("2019-01-31"),
            ): Combination(
                case="1",
                date_start="2019-01-01",
                date_end=False,
                last_date_invoiced=False,
                recurring_next_date="2019-01-01",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-01-01"),
                next_period_date_start=to_date("2019-01-01"),
                next_period_date_end=to_date("2019-01-15"),
            ): Combination(
                case="2",
                date_start="2019-01-01",
                date_end="2019-01-15",
                last_date_invoiced=False,
                recurring_next_date="2019-01-01",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-01-05"),
                next_period_date_start=to_date("2019-01-05"),
                next_period_date_end=to_date("2019-01-15"),
            ): Combination(
                case="3",
                date_start="2019-01-05",
                date_end="2019-01-15",
                last_date_invoiced=False,
                recurring_next_date="2019-01-05",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-01-05"),
                next_period_date_start=to_date("2019-01-01"),
                next_period_date_end=to_date("2019-01-15"),
            ): Combination(
                case="4",
                date_start="2019-01-01",
                date_end="2019-01-15",
                last_date_invoiced=False,
                recurring_next_date="2019-01-05",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-02-01"),
                next_period_date_start=to_date("2019-01-01"),
                next_period_date_end=to_date("2019-01-31"),
            ): Combination(
                case="5",
                date_start="2019-01-01",
                date_end=False,
                last_date_invoiced=False,
                recurring_next_date="2019-02-01",
                recurring_invoicing_type="post-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-02-01"),
                next_period_date_start=to_date("2019-01-01"),
                next_period_date_end=to_date("2019-01-15"),
            ): Combination(
                case="6",
                date_start="2019-01-01",
                date_end="2019-01-15",
                last_date_invoiced=False,
                recurring_next_date="2019-02-01",
                recurring_invoicing_type="post-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-02-01"),
                next_period_date_start=to_date("2019-01-05"),
                next_period_date_end=to_date("2019-01-31"),
            ): Combination(
                case="7",
                date_start="2019-01-05",
                date_end=False,
                last_date_invoiced=False,
                recurring_next_date="2019-02-01",
                recurring_invoicing_type="post-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-01-05"),
                next_period_date_start=to_date("2019-01-01"),
                next_period_date_end=to_date("2019-01-15"),
            ): Combination(
                case="8",
                date_start="2019-01-01",
                date_end="2019-01-15",
                last_date_invoiced=False,
                recurring_next_date="2019-01-05",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-01-01"),
                next_period_date_start=to_date("2018-12-16"),
                next_period_date_end=to_date("2019-01-31"),
            ): Combination(
                case="9",
                date_start="2018-01-01",
                date_end="2020-01-15",
                last_date_invoiced="2018-12-15",
                recurring_next_date="2019-01-01",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2019-01-01"),
                next_period_date_start=to_date("2018-12-16"),
                next_period_date_end=to_date("2018-12-31"),
            ): Combination(
                case="10",
                date_start="2018-01-01",
                date_end="2020-01-15",
                last_date_invoiced="2018-12-15",
                recurring_next_date="2019-01-01",
                recurring_invoicing_type="post-paid",
                recurring_rule_type="monthly",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2018-12-31"),
                next_period_date_start=to_date("2018-12-16"),
                next_period_date_end=to_date("2018-12-31"),
            ): Combination(
                case="11",
                date_start="2018-01-01",
                date_end="2020-01-15",
                last_date_invoiced="2018-12-15",
                recurring_next_date="2018-12-31",
                recurring_invoicing_type="post-paid",
                recurring_rule_type="monthlylastday",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2018-12-16"),
                next_period_date_start=to_date("2018-12-16"),
                next_period_date_end=to_date("2018-12-31"),
            ): Combination(
                case="12",
                date_start="2018-01-01",
                date_end="2020-01-15",
                last_date_invoiced="2018-12-15",
                recurring_next_date="2018-12-16",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthlylastday",
                recurring_interval=1,
                max_date_end=False,
            ),
            Result(
                recurring_next_date=to_date("2018-01-05"),
                next_period_date_start=to_date("2018-01-05"),
                next_period_date_end=to_date("2018-03-31"),
            ): Combination(
                case="12",
                date_start="2018-01-05",
                date_end="2020-01-15",
                last_date_invoiced=False,
                recurring_next_date="2018-01-05",
                recurring_invoicing_type="pre-paid",
                recurring_rule_type="monthlylastday",
                recurring_interval=3,
                max_date_end=False,
            ),
        }
        for result, combination in combinations.items():
            _update_contract_line(*combination)
            self.assertEqual(result, _get_result(), _error_message(*combination))

    def test_recurring_next_date(self):
        """recurring next date for a contract is the min for all lines"""
        self.contract.recurring_create_invoice()
        self.assertEqual(
            self.contract.recurring_next_date,
            min(self.contract.contract_line_ids.mapped("recurring_next_date")),
        )

    def test_cron_recurring_create_invoice(self):
        self.acct_line.date_start = "2018-01-01"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.date_end = "2018-03-15"
        contracts = self.contract2
        for _i in range(10):
            contracts |= self.contract.copy()
        self.env["contract.contract"].cron_recurring_create_invoice()
        invoice_lines = self.env["account.move.line"].search(
            [("contract_line_id", "in", contracts.mapped("contract_line_ids").ids)]
        )
        self.assertEqual(
            len(contracts.mapped("contract_line_ids")),
            len(invoice_lines),
        )

    def test_get_period_to_invoice_monthlylastday_postpaid(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_rule_type = "monthlylastday"
        self.acct_line.date_end = "2018-03-15"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-01-05"))
        self.assertEqual(last, to_date("2018-01-31"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-01"))
        self.assertEqual(last, to_date("2018-02-28"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-03-01"))
        self.assertEqual(last, to_date("2018-03-15"))

    def test_get_period_to_invoice_monthlylastday_prepaid(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_rule_type = "monthlylastday"
        self.acct_line.date_end = "2018-03-15"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-01-05"))
        self.assertEqual(last, to_date("2018-01-31"))
        self.assertEqual(recurring_next_date, to_date("2018-01-05"))
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-01-05"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-01"))
        self.assertEqual(last, to_date("2018-02-28"))
        self.assertEqual(recurring_next_date, to_date("2018-02-01"))
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-02-01"))
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-01-31"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-03-01"))
        self.assertEqual(last, to_date("2018-03-15"))
        self.assertEqual(recurring_next_date, to_date("2018-03-01"))
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2018-03-01"))
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-02-28"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertFalse(first)
        self.assertFalse(last)
        self.assertFalse(recurring_next_date)
        self.assertFalse(self.acct_line.recurring_next_date)
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2018-03-15"))

    def test_get_period_to_invoice_monthly_pre_paid_2(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_rule_type = "monthly"
        self.acct_line.date_end = "2018-08-15"
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-05"))
        self.assertEqual(last, to_date("2018-03-04"))
        self.acct_line.recurring_next_date = "2018-06-05"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-05"))
        self.assertEqual(last, to_date("2018-07-04"))

    def test_get_period_to_invoice_monthly_post_paid_2(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_rule_type = "monthly"
        self.acct_line.date_end = "2018-08-15"
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-05"))
        self.assertEqual(last, to_date("2018-03-04"))
        self.acct_line.recurring_next_date = "2018-06-05"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-05"))
        self.assertEqual(last, to_date("2018-06-04"))

    def test_get_period_to_invoice_monthly_post_paid(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_rule_type = "monthly"
        self.acct_line.date_end = "2018-03-15"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-01-05"))
        self.assertEqual(last, to_date("2018-02-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-05"))
        self.assertEqual(last, to_date("2018-03-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-03-05"))
        self.assertEqual(last, to_date("2018-03-15"))

    def test_get_period_to_invoice_monthly_pre_paid(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_rule_type = "monthly"
        self.acct_line.date_end = "2018-03-15"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-01-05"))
        self.assertEqual(last, to_date("2018-02-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-02-05"))
        self.assertEqual(last, to_date("2018-03-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-03-05"))
        self.assertEqual(last, to_date("2018-03-15"))

    def test_get_period_to_invoice_yearly_post_paid(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "post-paid"
        self.acct_line.recurring_rule_type = "yearly"
        self.acct_line.date_end = "2020-03-15"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-01-05"))
        self.assertEqual(last, to_date("2019-01-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2019-01-05"))
        self.assertEqual(last, to_date("2020-01-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2020-01-05"))
        self.assertEqual(last, to_date("2020-03-15"))

    def test_get_period_to_invoice_yearly_pre_paid(self):
        self.acct_line.date_start = "2018-01-05"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.recurring_rule_type = "yearly"
        self.acct_line.date_end = "2020-03-15"
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2018-01-05"))
        self.assertEqual(last, to_date("2019-01-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2019-01-05"))
        self.assertEqual(last, to_date("2020-01-04"))
        self.contract.recurring_create_invoice()
        first, last, recurring_next_date = self.acct_line._get_period_to_invoice(
            self.acct_line.last_date_invoiced,
            self.acct_line.recurring_next_date,
        )
        self.assertEqual(first, to_date("2020-01-05"))
        self.assertEqual(last, to_date("2020-03-15"))

    def test_check_last_date_invoiced_1(self):
        """
        start end can't be before the date of last invoice
        """
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    "last_date_invoiced": self.acct_line.date_start
                    - relativedelta(days=1)
                }
            )

    def test_check_last_date_invoiced_2(self):
        """
        start date can't be after the date of last invoice
        """
        self.acct_line.write({"date_end": self.today})
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {"last_date_invoiced": self.acct_line.date_end + relativedelta(days=1)}
            )

    def test_purchase_get_view(self):
        purchase_tree_view = self.env.ref("contract.contract_line_supplier_tree_view")
        purchase_form_view = self.env.ref("contract.contract_line_supplier_form_view")
        view = self.acct_line.with_context(default_contract_type="purchase").get_view(
            view_type="list"
        )
        self.assertEqual(view["id"], purchase_tree_view.id)
        view = self.acct_line.with_context(default_contract_type="purchase").get_view(
            view_type="form"
        )
        self.assertEqual(view["id"], purchase_form_view.id)

    def test_multicompany_partner_edited(self):
        """Editing a partner with contracts in several companies works."""
        company2 = self.env["res.company"].create({"name": "Company 2"})
        unprivileged_user = self.env["res.users"].create(
            {
                "name": "unprivileged test user",
                "login": "test",
                "company_id": company2.id,
                "company_ids": [(4, company2.id, False)],
            }
        )
        parent_partner = self.env["res.partner"].create(
            {"name": "parent partner", "is_company": True}
        )
        # Assume contract 2 is for company 2
        self.contract2.company_id = company2
        # Update the partner attached to both contracts
        self.partner.with_user(unprivileged_user).with_company(company2).with_context(
            company_id=company2.id
        ).write({"is_company": False, "parent_id": parent_partner.id})

    def test_sale_get_view(self):
        sale_form_view = self.env.ref("contract.contract_line_customer_form_view")
        view = self.acct_line.with_context(default_contract_type="sale").get_view(
            view_type="form"
        )
        self.assertEqual(view["id"], sale_form_view.id)

    def test_contract_count_invoice(self):
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.contract.recurring_create_invoice()
        self.contract._compute_invoice_count()
        self.assertEqual(self.contract.invoice_count, 3)

    def test_contract_count_invoice_2(self):
        invoices = self.env["account.move"]
        invoices |= self.contract.recurring_create_invoice()
        invoices |= self.contract.recurring_create_invoice()
        invoices |= self.contract.recurring_create_invoice()
        action = self.contract.action_show_invoices()
        self.assertEqual(set(action["domain"][0][2]), set(invoices.ids))

    def test_compute_create_invoice_visibility(self):
        self.assertTrue(self.contract.create_invoice_visibility)
        self.acct_line.write(
            {
                "date_start": "2018-01-01",
                "date_end": "2018-12-31",
                "last_date_invoiced": "2018-12-31",
                "recurring_next_date": False,
            }
        )
        self.assertFalse(self.acct_line.create_invoice_visibility)
        self.assertFalse(self.contract.create_invoice_visibility)
        section = self.env["contract.line"].create(
            {
                "contract_id": self.contract.id,
                "display_type": "line_section",
                "name": "Test section",
            }
        )
        self.assertFalse(section.create_invoice_visibility)

    def test_invoice_contract_without_lines(self):
        self.contract.contract_line_ids.unlink()
        self.assertFalse(self.contract.recurring_create_invoice())

    def test_check_last_date_invoiced_before_next_invoice_date(self):
        with self.assertRaises(ValidationError):
            self.acct_line.write(
                {
                    "date_start": "2019-01-01",
                    "date_end": "2019-12-01",
                    "recurring_next_date": "2019-01-01",
                    "last_date_invoiced": "2019-06-01",
                }
            )

    def test_recurrency_propagation(self):
        # Existing contract
        vals = {
            "recurring_rule_type": "yearly",
            "recurring_interval": 2,
            "date_start": to_date("2020-01-01"),
        }
        vals2 = vals.copy()
        vals2["line_recurrence"] = False
        self.contract.write(vals2)
        for field in vals:
            self.assertEqual(vals[field], self.acct_line[field])
        # New contract
        contract_form = Form(self.env["contract.contract"])
        contract_form.partner_id = self.partner
        contract_form.name = "Test new contract"
        contract_form.line_recurrence = False
        for field in vals:
            setattr(contract_form, field, vals[field])
        with contract_form.contract_line_fixed_ids.new() as line_form:
            line_form.product_id = self.product_1
        contract2 = contract_form.save()
        for field in vals:
            self.assertEqual(vals[field], contract2.contract_line_ids[field])

    def test_currency(self):
        currency_eur = self.env.ref("base.EUR")
        currency_cad = self.env.ref("base.CAD")
        # Get currency from company
        self.contract2.journal_id = False
        self.assertEqual(
            self.contract2.currency_id, self.contract2.company_id.currency_id
        )
        # Get currency from journal
        journal = self.env["account.journal"].create(
            {
                "name": "Test journal CAD",
                "code": "TCAD",
                "type": "sale",
                "currency_id": currency_cad.id,
            }
        )
        self.contract2.journal_id = journal.id
        self.assertEqual(self.contract2.currency_id, currency_cad)
        # Get currency from contract pricelist
        pricelist = self.env["product.pricelist"].create(
            {"name": "Test pricelist", "currency_id": currency_eur.id}
        )
        self.contract2.pricelist_id = pricelist.id
        self.contract2.contract_line_ids.automatic_price = True
        self.assertEqual(self.contract2.currency_id, currency_eur)
        # Get currency from partner pricelist
        self.contract2.pricelist_id = False
        self.contract2.partner_id.property_product_pricelist = pricelist.id
        pricelist.currency_id = currency_cad.id
        self.assertEqual(self.contract2.currency_id, currency_cad)
        # Assign manual currency
        self.contract2.manual_currency_id = currency_eur.id
        self.assertEqual(self.contract2.currency_id, currency_eur)
        # Assign same currency as computed one
        self.contract2.currency_id = currency_cad.id
        self.assertFalse(self.contract2.manual_currency_id)

    def test_contract_action_preview(self):
        action = self.contract.action_preview()
        self.assertIn("/my/contracts/", action["url"])
        self.assertIn("access_token=", action["url"])

    def test_recurring_create_invoice(self):
        self.acct_line.date_start = "2024-01-01"
        self.acct_line.recurring_invoicing_type = "pre-paid"
        self.acct_line.date_end = "2024-04-01"
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2024-01-31"))
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2024-02-01"))
        self.assertEqual(len(self.contract._get_related_invoices()), 1)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2024-02-29"))
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2024-03-01"))
        self.assertEqual(len(self.contract._get_related_invoices()), 2)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2024-03-31"))
        self.assertEqual(self.acct_line.recurring_next_date, to_date("2024-04-01"))
        self.assertEqual(len(self.contract._get_related_invoices()), 3)
        self.contract.recurring_create_invoice()
        self.assertEqual(self.acct_line.last_date_invoiced, to_date("2024-04-01"))
        self.assertFalse(self.acct_line.recurring_next_date)
        self.assertEqual(len(self.contract._get_related_invoices()), 4)
        self.contract.recurring_create_invoice()
        self.assertEqual(len(self.contract._get_related_invoices()), 4)

    @freeze_time("2023-05-01")
    def test_check_month_name_marker(self):
        """Set fixed date to check test correctly."""
        self.contract3.contract_line_ids.date_start = fields.Date.today()
        self.contract3.contract_line_ids.recurring_next_date = fields.Date.today()
        invoice_id = self.contract3.recurring_create_invoice()
        self.assertEqual(invoice_id.invoice_line_ids[0].name, "Header for May Services")
