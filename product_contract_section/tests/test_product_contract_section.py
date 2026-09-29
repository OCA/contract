# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests.common import TransactionCase


class TestProductContractSection(TransactionCase):
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
        cls.template_a = cls.env["contract.template"].create({"name": "Template A"})
        cls.template_b = cls.env["contract.template"].create({"name": "Template B"})
        cls.product_a = cls._create_contract_product("Product A", cls.template_a)
        cls.product_b = cls._create_contract_product("Product B", cls.template_b)
        cls.plain_product = cls.env["product.product"].create(
            {"name": "Plain", "type": "service"}
        )

    @classmethod
    def _create_contract_product(cls, name, template):
        product = cls.env["product.product"].create(
            {
                "name": name,
                "type": "service",
                "recurrence_number": 12,
                "recurrence_interval": "monthly",
                "recurring_interval": 1,
                "recurring_rule_type": "monthly",
                "recurring_invoicing_type": "pre-paid",
            }
        )
        product.with_company(cls.company).write(
            {
                "is_contract": True,
                "property_contract_template_id": template.id,
            }
        )
        return product

    def _create_order(self, lines_vals):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "order_line": [Command.create(vals) for vals in lines_vals],
            }
        )

    def _get_product_line_vals(self, product, sequence):
        return {
            "product_id": product.id,
            "product_uom_qty": 1,
            "sequence": sequence,
            "date_start": "2024-01-01",
        }

    def _generate_contracts(self, order):
        order.action_confirm()
        order.action_create_contract()

    def _get_contract(self, order, product):
        return order.order_line.filtered(
            lambda line, product=product: line.product_id == product
        ).contract_id

    def _upsell_order(self, contract, old_line, section_name):
        return self._create_order(
            [
                {
                    "display_type": "line_section",
                    "name": section_name,
                    "sequence": 10,
                },
                {
                    "product_id": self.product_a.id,
                    "product_uom_qty": 2,
                    "sequence": 20,
                    "date_start": "2024-06-01",
                    "contract_id": contract.id,
                    "contract_line_id": old_line.id,
                },
            ]
        )

    def _sections(self, contract):
        return contract.contract_line_ids.filtered(
            lambda line: line.display_type == "line_section"
        )

    def _notes(self, contract):
        return contract.contract_line_ids.filtered(
            lambda line: line.display_type == "line_note"
        )

    def test_section_spans_multiple_contracts(self):
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S", "sequence": 10},
                self._get_product_line_vals(self.product_a, 20),
                self._get_product_line_vals(self.product_b, 30),
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        contract_b = self._get_contract(order, self.product_b)
        self.assertTrue(contract_a)
        self.assertNotEqual(contract_a, contract_b)
        self.assertEqual(self._sections(contract_a).mapped("name"), ["S"])
        self.assertEqual(self._sections(contract_b).mapped("name"), ["S"])

    def test_note_attached_to_preceding_contract(self):
        # A note belongs to the product line above it.
        order = self._create_order(
            [
                self._get_product_line_vals(self.product_a, 10),
                {"display_type": "line_note", "name": "N", "sequence": 20},
                self._get_product_line_vals(self.product_b, 30),
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        contract_b = self._get_contract(order, self.product_b)
        self.assertEqual(self._notes(contract_a).mapped("name"), ["N"])
        self.assertFalse(self._notes(contract_b))

    def test_section_span_stops_at_next_section(self):
        # A section only spans the products up to the next section, so the
        # first section is not propagated to the second section's contract.
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S1", "sequence": 10},
                self._get_product_line_vals(self.product_a, 20),
                {"display_type": "line_section", "name": "S2", "sequence": 30},
                self._get_product_line_vals(self.product_b, 40),
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        contract_b = self._get_contract(order, self.product_b)
        self.assertEqual(self._sections(contract_a).mapped("name"), ["S1"])
        self.assertEqual(self._sections(contract_b).mapped("name"), ["S2"])

    def test_note_without_product_above_not_propagated(self):
        # A note with no product line above it (only a section) has nothing to
        # attach to and is dropped.
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S", "sequence": 10},
                {"display_type": "line_note", "name": "N", "sequence": 20},
                self._get_product_line_vals(self.product_a, 30),
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        self.assertFalse(self._notes(contract_a))
        self.assertEqual(self._sections(contract_a).mapped("name"), ["S"])

    def test_section_and_note_same_contract(self):
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S", "sequence": 10},
                self._get_product_line_vals(self.product_a, 20),
                {"display_type": "line_note", "name": "N", "sequence": 30},
                self._get_product_line_vals(self.product_a, 40),
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        display_lines = contract_a.contract_line_ids.filtered("display_type")
        self.assertEqual(display_lines.mapped("name"), ["S", "N"])

    def test_propagation_is_idempotent(self):
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S", "sequence": 10},
                self._get_product_line_vals(self.product_a, 20),
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        self.assertEqual(len(self._sections(contract_a)), 1)
        # Running the generation again must not duplicate the section.
        order.action_create_contract()
        self.assertEqual(len(self._sections(contract_a)), 1)

    def test_trailing_section_without_products_not_propagated(self):
        order = self._create_order(
            [
                self._get_product_line_vals(self.product_a, 10),
                {"display_type": "line_section", "name": "T", "sequence": 20},
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        self.assertFalse(self._sections(contract_a))

    def test_upsell_does_not_duplicate_existing_section(self):
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S", "sequence": 10},
                self._get_product_line_vals(self.product_a, 20),
            ]
        )
        self._generate_contracts(order)
        contract = self._get_contract(order, self.product_a)
        old_line = contract.contract_line_ids.filtered(
            lambda line: not line.display_type
        )
        upsell = self._upsell_order(contract, old_line, "S")
        upsell.action_confirm()
        upsell.action_create_contract()
        self.assertEqual(len(self._sections(contract)), 1)

    def test_upsell_adds_new_section(self):
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S", "sequence": 10},
                self._get_product_line_vals(self.product_a, 20),
            ]
        )
        self._generate_contracts(order)
        contract = self._get_contract(order, self.product_a)
        old_line = contract.contract_line_ids.filtered(
            lambda line: not line.display_type
        )
        upsell = self._upsell_order(contract, old_line, "Extra")
        upsell.action_confirm()
        upsell.action_create_contract()
        self.assertEqual(
            sorted(self._sections(contract).mapped("name")), ["Extra", "S"]
        )

    def test_section_over_non_contract_product_not_propagated(self):
        order = self._create_order(
            [
                {"display_type": "line_section", "name": "S", "sequence": 10},
                {
                    "product_id": self.plain_product.id,
                    "product_uom_qty": 1,
                    "sequence": 20,
                },
                self._get_product_line_vals(self.product_a, 30),
            ]
        )
        self._generate_contracts(order)
        contract_a = self._get_contract(order, self.product_a)
        # The section spans the plain product too, but that product creates no
        # contract line, so the section is only propagated to contract A.
        self.assertEqual(self._sections(contract_a).mapped("name"), ["S"])
