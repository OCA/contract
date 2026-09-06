# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import itertools
from unittest.mock import patch

from odoo import Command
from odoo.tests.common import TransactionCase

from odoo.addons.contract.models.contract_line import ContractLine

FLAG_NAMES = [
    "show_details",
    "show_subtotal",
    "show_section_subtotal",
    "show_line_amount",
]


class TestContractLayoutCategoryHideDetail(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company
        cls.company.create_contract_at_sale_order_confirmation = False
        cls.pricelist = cls.env["product.pricelist"].create({"name": "Test pricelist"})
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Service", "type": "service", "list_price": 100.0}
        )
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Hide Detail Contract",
                "partner_id": cls.partner.id,
                "pricelist_id": cls.pricelist.id,
                "line_recurrence": False,
                "contract_type": "sale",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2024-01-15",
                "contract_line_ids": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "Section",
                            "show_details": False,
                            "show_subtotal": False,
                            "show_section_subtotal": False,
                            "show_line_amount": False,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": cls.product.id,
                            "name": "Service line",
                            "quantity": 1,
                            "price_unit": 100.0,
                        }
                    ),
                ],
            }
        )
        cls.section = cls.contract.contract_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )

    def test_flags_default_true(self):
        section = self.env["contract.line"].create(
            {
                "contract_id": self.contract.id,
                "display_type": "line_section",
                "name": "Default section",
            }
        )
        self.assertTrue(section.show_details)
        self.assertTrue(section.show_subtotal)
        self.assertTrue(section.show_section_subtotal)
        self.assertTrue(section.show_line_amount)

    def test_flags_available_on_template_line(self):
        template = self.env["contract.template"].create({"name": "T"})
        line = self.env["contract.template.line"].create(
            {
                "contract_id": template.id,
                "display_type": "line_section",
                "name": "Section",
                "show_details": False,
            }
        )
        self.assertFalse(line.show_details)
        self.assertTrue(line.show_subtotal)

    def test_prepare_invoice_line_propagates_flags(self):
        self.contract.recurring_create_invoice()
        invoice = self.contract._get_related_invoices()
        self.assertTrue(invoice)
        section_line = invoice.invoice_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )
        self.assertTrue(section_line)
        self.assertFalse(section_line.show_details)
        self.assertFalse(section_line.show_subtotal)
        self.assertFalse(section_line.show_section_subtotal)
        self.assertFalse(section_line.show_line_amount)

    def test_prepare_invoice_line_keeps_empty_result(self):
        # An extension may nullify a line by returning an empty dict from
        # _prepare_invoice_line; our flag update must not turn it back into a
        # real invoice line.
        line = self.contract.contract_line_ids.filtered(
            lambda contract_line: not contract_line.display_type
        )
        with patch.object(ContractLine, "_prepare_invoice_line", return_value={}):
            self.assertEqual(line._prepare_invoice_line(), {})

    def test_report_renders_with_hidden_section(self):
        html = self.env["ir.actions.report"]._render_qweb_html(
            "contract.report_contract", self.contract.ids
        )[0]
        self.assertTrue(html)

    def test_so_flags_propagated_to_contract_section(self):
        template = self.env["contract.template"].create({"name": "Template"})
        product = self.env["product.product"].create(
            {
                "name": "Contract product",
                "type": "service",
                "recurrence_number": 12,
                "recurrence_interval": "monthly",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "recurring_invoicing_type": "pre-paid",
            }
        )
        product.with_company(self.company).write(
            {"is_contract": True, "property_contract_template_id": template.id}
        )
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [
                    Command.create(
                        {
                            "display_type": "line_section",
                            "name": "S",
                            "sequence": 10,
                            "show_details": False,
                            "show_line_amount": False,
                        }
                    ),
                    Command.create(
                        {
                            "product_id": product.id,
                            "product_uom_qty": 1,
                            "sequence": 20,
                            "date_start": "2024-01-01",
                        }
                    ),
                ],
            }
        )
        order.action_confirm()
        order.action_create_contract()
        contract = order.order_line.filtered("product_id").contract_id
        section = contract.contract_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )
        self.assertEqual(len(section), 1)
        self.assertFalse(section.show_details)
        self.assertFalse(section.show_line_amount)
        # Untouched flags keep their default.
        self.assertTrue(section.show_subtotal)

    # -- Report rendering ---------------------------------------------------

    def _section_vals(self, name, sequence, **flags):
        return {
            "display_type": "line_section",
            "name": name,
            "sequence": sequence,
            **flags,
        }

    def _line_vals(self, name, price, sequence):
        return {
            "product_id": self.product.id,
            "name": name,
            "quantity": 1,
            "price_unit": price,
            "sequence": sequence,
        }

    def _build_contract(self, lines_vals):
        return self.env["contract.contract"].create(
            {
                "name": "Report Contract",
                "partner_id": self.partner.id,
                "pricelist_id": self.pricelist.id,
                "line_recurrence": False,
                "contract_type": "sale",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "date_start": "2024-01-15",
                "contract_line_ids": [Command.create(vals) for vals in lines_vals],
            }
        )

    def _render_report(self, contract):
        html = self.env["ir.actions.report"]._render_qweb_html(
            "contract.report_contract", contract.ids
        )[0]
        return html.decode() if isinstance(html, bytes) else html

    def test_report_renders_for_every_option_combination(self):
        for combo in itertools.product([True, False], repeat=len(FLAG_NAMES)):
            section_flags = dict(zip(FLAG_NAMES, combo, strict=False))
            contract = self._build_contract(
                [
                    self._section_vals("VisibleSection", 10, **section_flags),
                    self._line_vals("Line A", 100.0, 20),
                    self._line_vals("Line B", 37.0, 30),
                ]
            )
            html = self._render_report(contract)
            self.assertTrue(html)
            # The section header stays visible whatever the options are.
            self.assertIn("VisibleSection", html)

    def test_report_hides_details_when_disabled(self):
        contract = self._build_contract(
            [
                self._section_vals("VisibleSection", 10, show_details=False),
                self._line_vals("SecretLine", 100.0, 20),
            ]
        )
        html = self._render_report(contract)
        self.assertIn("VisibleSection", html)
        self.assertNotIn("SecretLine", html)

    def test_report_shows_details_when_enabled(self):
        contract = self._build_contract(
            [
                self._section_vals("VisibleSection", 10, show_details=True),
                self._line_vals("SecretLine", 100.0, 20),
            ]
        )
        html = self._render_report(contract)
        self.assertIn("SecretLine", html)

    def test_report_subtotal_accumulation(self):
        # Alpha groups 100 + 37 = 137, distinct from the grand total (147) and
        # from every individual line, so its presence proves accumulation.
        contract = self._build_contract(
            [
                self._section_vals("Alpha", 10, show_details=True, show_subtotal=True),
                self._line_vals("AlphaOne", 100.0, 20),
                self._line_vals("AlphaTwo", 37.0, 30),
                self._section_vals("Beta", 40, show_details=True, show_subtotal=True),
                self._line_vals("BetaOne", 10.0, 50),
            ]
        )
        html = self._render_report(contract)
        self.assertIn("137", html)

    def test_report_section_subtotal_shown_when_details_hidden(self):
        contract = self._build_contract(
            [
                self._section_vals(
                    "Alpha", 10, show_details=False, show_section_subtotal=True
                ),
                self._line_vals("AlphaOne", 100.0, 20),
                self._line_vals("AlphaTwo", 37.0, 30),
                self._section_vals(
                    "Beta", 40, show_details=False, show_section_subtotal=True
                ),
                self._line_vals("BetaOne", 10.0, 50),
            ]
        )
        html = self._render_report(contract)
        # Details are hidden but the collapsed section subtotal is shown.
        self.assertNotIn("AlphaOne", html)
        self.assertIn("137", html)

    def test_report_section_subtotal_hidden_when_disabled(self):
        # Alpha subtotal (137) must not appear when both the subtotal and the
        # collapsed section subtotal are disabled.
        contract = self._build_contract(
            [
                self._section_vals(
                    "Alpha",
                    10,
                    show_details=False,
                    show_section_subtotal=False,
                ),
                self._line_vals("AlphaOne", 100.0, 20),
                self._line_vals("AlphaTwo", 37.0, 30),
                self._section_vals("Beta", 40),
                self._line_vals("BetaOne", 10.0, 50),
            ]
        )
        html = self._render_report(contract)
        self.assertNotIn("137", html)
