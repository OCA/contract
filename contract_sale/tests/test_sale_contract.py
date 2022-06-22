# Copyright 2022 ForgeFlow - Joan Mateu
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)


from odoo.tests.common import TransactionCase


class TestSaleContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleContract, cls).setUpClass()

        cls.user_sales_all_documents = cls.env["res.users"].create(
            {
                "name": "user rights all documents ",
                "login": "test1",
                "groups_id": [
                    (6, 0, [cls.env.ref("sales_team.group_sale_salesman_all_leads").id])
                ],
            }
        )
        cls.user_sales_own_documents = cls.env["res.users"].create(
            {
                "name": "user rights own documents ",
                "login": "test2",
                "groups_id": [
                    (6, 0, [cls.env.ref("sales_team.group_sale_salesman").id])
                ],
            }
        )

        cls.pricelist = cls.env["product.pricelist"].create(
            {"name": "pricelist for contract test"}
        )

        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test contract partner",
                "property_product_pricelist": cls.pricelist.id,
            }
        )

    def _create_contract(self, user):
        self.contract = (
            self.env["contract.contract"]
            .with_user(user)
            .create(
                {
                    "name": "Test Contract",
                    "partner_id": self.partner.id,
                    "pricelist_id": self.partner.property_product_pricelist.id,
                    "line_recurrence": False,
                    "contract_type": "sale",
                    "recurring_interval": 1,
                    "recurring_rule_type": "monthly",
                    "date_start": "2018-02-15",
                    "contract_line_ids": [],
                }
            )
        )

    def test_01_create_contract_with_sale_perm_not_acc(self):
        self._create_contract(self.user_sales_all_documents)

        contracts = (
            self.env["contract.contract"]
            .with_user(self.user_sales_all_documents)
            .search([])
        )
        self.assertEqual(len(contracts), 1)

    def test_02_see_just_own_contracts(self):
        self._create_contract(self.user_sales_all_documents)
        self._create_contract(self.user_sales_all_documents)
        self._create_contract(self.user_sales_own_documents)
        self._create_contract(self.user_sales_own_documents)

        contracts = (
            self.env["contract.contract"]
            .with_user(self.user_sales_own_documents)
            .search([])
        )
        self.assertEqual(len(contracts), 2)

    def test_03_see_all_contracts(self):
        self._create_contract(self.user_sales_all_documents)
        self._create_contract(self.user_sales_all_documents)
        self._create_contract(self.user_sales_own_documents)
        self._create_contract(self.user_sales_own_documents)
        contracts = (
            self.env["contract.contract"]
            .with_user(self.user_sales_all_documents)
            .search([])
        )
        self.assertEqual(len(contracts), 4)

    def test_04_edit_existing_contract(self):
        self._create_contract(self.user_sales_own_documents)
        contract_modify = (
            self.env["contract.contract"]
            .with_user(self.user_sales_own_documents)
            .search([])
        )
        self.assertEqual(len(contract_modify), 1)
        self.assertEqual(contract_modify.name, "Test Contract")

        self.env["contract.contract"].with_user(self.user_sales_own_documents).search(
            []
        ).write(
            {
                "name": "Test_contract_to_modify",
            }
        )
        contract_modify = (
            self.env["contract.contract"]
            .with_user(self.user_sales_own_documents)
            .search([])
        )
        self.assertEqual(contract_modify.name, "Test_contract_to_modify")
