# Copyright 2024 Foodles (https://www.foodles.co/).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo.tests import TransactionCase


class TestContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.customer = cls.env["res.partner"].create({"name": "Test Customer"})
        cls.contract = cls.env["contract.contract"].create(
            {"name": "Test Contract", "partner_id": cls.customer.id}
        )

    @patch("odoo.addons.contract_exception.models.contract.Contract.detect_exceptions")
    @patch(
        "odoo.addons.contract_exception."
        "models.contract.Contract._fields_trigger_check_exception"
    )
    def test_contract_check_exception_with_field_that_trigger_exception(
        self, mock_fields_trigger_check_exception, mock_detect_exceptions
    ):
        mock_fields_trigger_check_exception.return_value = ["partner_id"]
        self.contract._contract_check_exception({"partner_id": 1})
        mock_detect_exceptions.assert_called_once()

    @patch("odoo.addons.contract_exception.models.contract.Contract.detect_exceptions")
    @patch(
        "odoo.addons.contract_exception."
        "models.contract.Contract._fields_trigger_check_exception"
    )
    def test_contract_check_exception_without_field_that_trigger_exception(
        self, mock_fields_trigger_check_exception, mock_detect_exceptions
    ):
        mock_fields_trigger_check_exception.return_value = []
        self.contract._contract_check_exception({"partner_id": 1})
        self.assertEqual(mock_detect_exceptions.call_count, 0)

    def test_detect_exceptions(self):
        rules = self.env["exception.rule"].create(
            [
                {
                    "name": "Test Rule",
                    "model": "contract.contract",
                    "code": "failed=True",
                },
                {
                    "name": "Test contract line Rule",
                    "model": "contract.line",
                    "code": "failed=True",
                },
            ]
        )
        self.contract.contract_line_ids = [(0, 0, {"name": "Test Line"})]
        exceptions = self.contract.detect_exceptions()
        self.assertEqual(exceptions, rules.ids)

    @patch("odoo.addons.contract_exception.models.contract.Contract.detect_exceptions")
    def test_all_contracts(self, mock_detect_exceptions):
        self.env["contract.contract"].test_all_contracts()
        self.assertEqual(
            self.env["contract.contract"].search_count([]),
            mock_detect_exceptions.call_count,
        )
