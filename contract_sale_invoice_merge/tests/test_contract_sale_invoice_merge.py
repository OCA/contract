# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestContractSaleInvoiceMerge(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                queue_job__no_delay=True,  # no jobs thanks
            )
        )

        cls.cron = cls.env.ref(
            "contract_sale_invoice_merge.contract_sale_invoice_merge_cron"
        )
        cls.cron.method_direct_trigger()

        cls.today = fields.Date.today()

        cls.partner = cls.env["res.partner"].create({"name": "Partner"})
        cls.partner2 = cls.env["res.partner"].create({"name": "Partner2"})
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product",
                "list_price": 50.0,
            }
        )
        cls.product2 = cls.env["product.product"].create(
            {
                "name": "Product2",
                "list_price": 75.0,
            }
        )
        cls.product3 = cls.env["product.product"].create(
            {
                "name": "Product3",
                "list_price": 100.0,
            }
        )
        cls.contract_tmpl = cls.env["contract.template"].create({"name": "CT"})
        cls.product4 = cls.env["product.product"].create(
            {
                "name": "Product4",
                "type": "service",
                "list_price": 20.0,
                "is_contract": True,
                "recurrence_number": 6,
                "property_contract_template_id": cls.contract_tmpl.id,
            }
        )
        cls.journal = cls.env["account.journal"].search(
            [("code", "=", "INV"), ("company_id", "=", cls.env.company.id)], limit=1
        )
        cls.order = cls.env["sale.order"].create(
            {
                "name": "Sale Order",
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "journal_id": cls.journal.id,
            }
        )
        cls.order2 = cls.env["sale.order"].create(
            {
                "name": "Sale Order 2",
                "partner_id": cls.partner.id,
                "partner_invoice_id": cls.partner.id,
                "journal_id": cls.journal.id,
            }
        )
        cls.order_lines = cls.env["sale.order.line"].create(
            [
                {
                    "order_id": cls.order.id,
                    "product_id": cls.product.id,
                },
                {
                    "order_id": cls.order2.id,
                    "product_id": cls.product2.id,
                },
                {
                    "order_id": cls.order2.id,
                    "product_id": cls.product3.id,
                },
            ]
        )

    def _trigger_cron(self):
        old_moves = self.env["account.move"].search([])
        self.cron.method_direct_trigger()
        return self.env["account.move"].search([]) - old_moves

    def test_cron_exists(self):
        self.assertTrue(self.cron.exists())

    def test_cron_runs_on_empty(self):
        move = self._trigger_cron()
        self.assertFalse(move)

    def test_cron_invoices_single_order(self):
        self.order.action_confirm()
        self.assertEqual(self.order.invoice_status, "to invoice")
        move = self._trigger_cron()
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.assertEqual(len(move), 1)
        self.assertAlmostEqual(move.amount_untaxed, 50)
        move_line = move.invoice_line_ids
        self.assertEqual(len(move_line), 1)
        self.assertAlmostEqual(move_line.price_unit, 50)
        self.assertEqual(move_line.sale_line_ids, self.order_lines[0])

    def test_cron_invoices_multi_order_grouped(self):
        self.order.action_confirm()
        self.order2.action_confirm()
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.assertEqual(self.order2.invoice_status, "to invoice")
        move = self._trigger_cron()
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.assertEqual(self.order2.invoice_status, "invoiced")
        self.assertEqual(len(move), 1)
        self.assertAlmostEqual(move.amount_untaxed, 225)
        self.assertIn("Sale Order", move.invoice_origin)
        self.assertIn("Sale Order 2", move.invoice_origin)
        move_lines = move.invoice_line_ids
        self.assertEqual(len(move_lines), 3)
        self.assertEqual(move_lines.sale_line_ids, self.order_lines)

    def test_cron_invoices_multi_order_not_grouped(self):
        # Cron should create 2 separate moves
        self.order2.partner_invoice_id = self.partner2

        self.order.action_confirm()
        self.order2.action_confirm()
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.assertEqual(self.order2.invoice_status, "to invoice")
        moves = self._trigger_cron()
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.assertEqual(self.order2.invoice_status, "invoiced")
        self.assertEqual(len(moves), 2)
        move1 = moves.filtered_domain(
            [("invoice_line_ids.sale_line_ids", "=", self.order_lines[0].id)]
        )
        move2 = moves - move1
        self.assertAlmostEqual(move1.amount_untaxed, 50)
        self.assertEqual(len(move1.invoice_line_ids), 1)
        self.assertEqual(move1.invoice_line_ids.sale_line_ids, self.order_lines[0])
        self.assertAlmostEqual(move2.amount_untaxed, 175)
        self.assertEqual(len(move2.invoice_line_ids), 2)
        self.assertEqual(move2.invoice_line_ids.sale_line_ids, self.order_lines[1:])

    def test_cron_invoices_multi_order_do_not_group_move(self):
        self.order2.do_not_group_move = True

        self.order.action_confirm()
        self.order2.action_confirm()
        self.assertEqual(self.order.invoice_status, "to invoice")
        self.assertEqual(self.order2.invoice_status, "to invoice")
        moves = self._trigger_cron()
        self.assertEqual(self.order.invoice_status, "invoiced")
        self.assertEqual(self.order2.invoice_status, "invoiced")
        self.assertEqual(len(moves), 2)
        move1 = moves.filtered_domain(
            [("invoice_line_ids.sale_line_ids", "=", self.order_lines[0].id)]
        )
        move2 = moves - move1
        self.assertAlmostEqual(move1.amount_untaxed, 50)
        self.assertEqual(len(move1.invoice_line_ids), 1)
        self.assertEqual(move1.invoice_line_ids.sale_line_ids, self.order_lines[0])
        self.assertAlmostEqual(move2.amount_untaxed, 175)
        self.assertEqual(len(move2.invoice_line_ids), 2)
        self.assertEqual(move2.invoice_line_ids.sale_line_ids, self.order_lines[1:])

    def test_cron_invoices_single_contract(self):
        contract = self.env["contract.contract"].create(
            {
                "name": "Contract",
                "partner_id": self.partner.id,
            }
        )
        contract_line = self.env["contract.line"].create(
            {
                "name": "Contract Line",
                "contract_id": contract.id,
                "product_id": self.product4.id,
            }
        )
        move = self._trigger_cron()
        self.assertEqual(len(move), 1)
        self.assertEqual(move.invoice_line_ids.contract_line_id, contract_line)

    def test_cron_invoices_single_contract_recurring(self):
        contract = self.env["contract.contract"].create(
            {
                "name": "Contract",
                "partner_id": self.partner.id,
            }
        )
        contract_line = self.env["contract.line"].create(
            {
                "name": "Contract Line",
                "contract_id": contract.id,
                "product_id": self.product4.id,
                "date_start": self.today - relativedelta(months=2),
            }
        )
        moves = self._trigger_cron()
        self.assertEqual(len(moves), 3)
        self.assertEqual(moves.invoice_line_ids.contract_line_id, contract_line)

    def test_cron_invoices_multi_contract_recurring(self):
        contracts = self.env["contract.contract"].create(
            [
                {
                    "name": "Contract",
                    "partner_id": self.partner.id,
                },
                {
                    "name": "Contract 2",
                    "partner_id": self.partner.id,
                },
            ]
        )
        contract_lines = self.env["contract.line"].create(
            [
                {
                    "name": "Contract Line",
                    "contract_id": contracts[0].id,
                    "product_id": self.product4.id,
                },
                {
                    "name": "Contract Line 2",
                    "contract_id": contracts[0].id,
                    "product_id": self.product4.id,
                    "date_start": self.today - relativedelta(months=2),
                },
                {
                    "name": "Contract 2 Line",
                    "contract_id": contracts[1].id,
                    "product_id": self.product4.id,
                    "date_start": self.today - relativedelta(months=1),
                },
            ]
        )

        moves = self._trigger_cron()
        self.assertEqual(len(moves), 3)
        self.assertEqual(moves.invoice_line_ids.contract_line_id, contract_lines)
        move1 = moves.filtered(
            lambda s: contract_lines[0] in s.invoice_line_ids.contract_line_id
        )
        self.assertEqual(len(move1), 1)
        self.assertEqual(len(move1.invoice_line_ids), 3)
        self.assertEqual(move1.invoice_line_ids.contract_line_id, contract_lines)
        moves_CL2 = moves.filtered(
            lambda s: contract_lines[1] in s.invoice_line_ids.contract_line_id
        )
        self.assertEqual(len(moves_CL2), 3)
        moves_CL3 = moves.filtered(
            lambda s: contract_lines[2] in s.invoice_line_ids.contract_line_id
        )
        self.assertEqual(len(moves_CL3), 2)
        move2 = moves_CL3 - move1
        self.assertEqual(len(move2), 1)
        self.assertEqual(len(move2.invoice_line_ids), 2)
        self.assertEqual(move2.invoice_line_ids.contract_line_id, contract_lines[1:])

    def test_cron_invoices_order_and_contract_grouped(self):
        order_line_contract = self.env["sale.order.line"].create(
            {
                "order_id": self.order.id,
                "product_id": self.product4.id,
            }
        )
        self.order.action_confirm()
        contract = order_line_contract.contract_id
        self.assertEqual(self.order.invoice_status, "to invoice")
        move = self._trigger_cron()
        self.assertEqual(self.order.invoice_status, "no")
        self.assertEqual(len(move), 1)
        self.assertAlmostEqual(move.amount_untaxed, 70)
        self.assertIn("Sale Order", move.invoice_origin)
        self.assertIn(contract.name, move.invoice_origin)
        move_lines = move.invoice_line_ids
        self.assertEqual(len(move_lines), 2)
        contract_move_line = move_lines.filtered(lambda s: s.contract_line_id)
        self.assertEqual(len(contract_move_line), 1)
        self.assertAlmostEqual(contract_move_line.price_unit, 20)
        self.assertEqual(contract_move_line.sale_line_ids, order_line_contract)
        order_move_line = move_lines - contract_move_line
        self.assertAlmostEqual(order_move_line.price_unit, 50)
        self.assertEqual(order_move_line.sale_line_ids, self.order_lines[0])
