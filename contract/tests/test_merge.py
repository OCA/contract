# Copyright 2025 Simone Rubino - PyTech
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from .test_contract import TestContractBase


class TestMergeBase(TestContractBase):
    def _run_wizard(self, contracts):
        """Run the merge wizard for `contracts`."""
        result_contract_action = (
            self.env["contract.merge"]
            .with_context(active_ids=contracts.ids)
            .create({})
            .run()
        )
        result_contract = self.env[result_contract_action["res_model"]].browse(
            result_contract_action["res_id"]
        )
        return result_contract


class TestMerge(TestMergeBase):
    def test_merged_lines(self):
        """The merged contract has the lines of merged contracts."""
        # Arrange
        contract = self.contract
        contract_line = contract.contract_line_ids
        other_contract = contract.copy()
        other_contract_line = other_contract.contract_line_ids
        # pre-condition
        self.assertEqual(len(contract_line), 1)
        self.assertEqual(len(other_contract_line), 1)
        self.assertNotEqual(contract_line, other_contract_line)

        # Act
        result_contract = self._run_wizard(contract | other_contract)

        # Assert
        self.assertCountEqual(
            result_contract.contract_line_ids,
            contract_line | other_contract_line,
        )
