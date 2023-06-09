# Copyright 2023 Foodles (https://www.foodles.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.contract.tests.test_contract import TestContractBase


@tagged("post_install", "-at_install")
class TestContractSplit(TestContractBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_default_get(self):
        wizard = (
            self.env["split.contract"]
            .with_context(active_id=self.contract3.id)
            .create({})
        )
        self.assertEqual(self.contract3.partner_id.id, wizard.partner_id.id)
        self.assertEqual(
            self.contract3.invoice_partner_id.id, wizard.invoice_partner_id.id
        )
        self.assertEqual(self.contract3.id, wizard.main_contract_id.id)
        self.assertEqual(3, len(wizard.split_line_ids.ids))

    def test_no_split_because_no_qty_set(self):
        wizard = (
            self.env["split.contract"]
            .with_context(active_id=self.contract3.id)
            .create({})
        )
        wizard.partner_id = self.partner_2.id
        initial_contracts_length = self.env["contract.contract"].search_count([])
        # confirm wizard without setting to_split quantities
        wizard.action_split_contract()
        # nothing should have changed. No new contract created and original
        # contract remains untouched
        self.assertEqual(3, len(self.contract3.contract_line_ids.ids))
        self.assertEqual(
            initial_contracts_length, self.env["contract.contract"].search_count([])
        )

    def test_split_one_line_full_qty(self):
        wizard = (
            self.env["split.contract"]
            .with_context(active_id=self.contract3.id)
            .create({})
        )
        wizard.partner_id = self.partner_2.id
        initial_contracts_length = self.env["contract.contract"].search_count([])
        # set quantity to split in the wizard
        wizard.split_line_ids[0].quantity_to_split = wizard.split_line_ids[
            0
        ].original_qty
        # confirm wizard with setting to_split quantities
        new_contract = wizard.action_split_contract()
        # A new contract must have been created.
        self.assertEqual(
            initial_contracts_length + 1, self.env["contract.contract"].search_count([])
        )
        # new contract has now the splitted line
        self.assertEqual(self.partner2.id, new_contract.partner_id.id)
        self.assertEqual(1, len(new_contract.contract_line_ids.ids))
        self.assertEqual(
            self.contract3.id,
            new_contract.contract_line_ids.mapped("splitted_from_contract_id"),
        )
        # Original contract has now only 2 lines (3 at the beginning)
        self.assertEqual(2, len(self.contract3.contract_line_ids.ids))

    def test_split_one_line_one_qty(self):
        # Set a qty = 2 in one line of a contract
        self.contract3.contract_line_ids.filtered(
            lambda line: line.name == "Line"
        ).quantity = 2
        wizard = (
            self.env["split.contract"]
            .with_context(active_id=self.contract3.id)
            .create({})
        )
        wizard.partner_id = self.partner_2.id
        initial_contracts_length = self.env["contract.contract"].search_count([])
        # set quantity to split in the wizard
        wizard.split_line_ids.filtered(lambda l: l.name == "Line").quantity_to_split = 1
        # confirm wizard with setting to_split quantities
        new_contract = wizard.action_split_contract()
        # A new contract must have been created.
        self.assertEqual(
            initial_contracts_length + 1, self.env["contract.contract"].search_count([])
        )
        # new contract has partner2 as partner_id
        self.assertEqual(self.partner2.id, new_contract.partner_id.id)
        # new contract has now the splitted line with a qty of one
        self.assertEqual(1, len(new_contract.contract_line_ids.ids))
        self.assertEqual(1, new_contract.contract_line_ids.quantity)
        self.assertEqual(
            self.contract3.id,
            new_contract.contract_line_ids.mapped("splitted_from_contract_id"),
        )
        # Original contract still has 3 lines but with a qty=1 in the last line named "Line"
        self.assertEqual(3, len(self.contract3.contract_line_ids.ids))
        self.assertEqual(
            1,
            self.contract3.contract_line_ids.filtered(
                lambda l: l.name == "Line"
            ).quantity,
        )

    def test_split_with_more_quantity_should_raise_error(self):
        wizard = (
            self.env["split.contract"]
            .with_context(active_id=self.contract3.id)
            .create({})
        )
        # set quantity to split in the wizard
        wizard.split_line_ids[0].quantity_to_split = (
            wizard.split_line_ids[0].original_qty + 2
        )
        # confirm wizard with setting to_split quantities that should raise an error
        with self.assertRaises(ValidationError):
            wizard.action_split_contract()
