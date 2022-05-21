# Copyright 2022 Andrea Cometa - Apulia Software (www.apuliasoftware.it)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged

from ..hooks import pre_init_hook


@tagged("post_install", "-at_install")
class TestContractSequence(TransactionCase):
    """Tests for creating Contract with and without Sequence"""

    def setUp(self):
        super(TestContractSequence, self).setUp()
        self.contract_contract = self.env["contract.contract"]
        self.contract_template = self.env["contract.template"].create(
            {
                "name": "Test contract template",
            }
        )
        self.pricelist = self.env["product.pricelist"].create(
            {
                "name": "pricelist for contract test",
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "partner test contract",
                "property_product_pricelist": self.pricelist.id,
                "email": "demo@demo.com",
            }
        )

    def test_onchange_company(self):
        """Test that company sequence is correctly filled"""
        company = self.env["res.company"].new({"name": "Fake Company"})
        company.contract_default_sequence = False
        self.env["res.config.settings"].onchange_company_id()
        self.assertTrue(company.contract_default_sequence is not False)

    def test_contract_create_with_manual_code(self):
        contract = self.contract_contract.create(
            {
                "name": "C/22/0001",
                "code": "Contract with manual code",
                "partner_id": self.partner.id,
            }
        )
        self.assertEqual(contract.name, "C/22/0001")
        contract_new = self.contract_contract.create(
            {
                "code": "Contract with template",
                "partner_id": self.partner.id,
                "contract_template_id": self.contract_template.id,
            }
        )
        self.assertTrue(contract_new.name)

    def test_contract_create_without_code(self):
        contract_1 = self.contract_contract.create(
            {
                "code": "Contract nr 1",
                "name": "/",
                "partner_id": self.partner.id,
            }
        )
        self.assertRegex(str(contract_1.name), r"CON/*")

    def test_contract_copy(self):
        contract_2 = self.contract_contract.create(
            {
                "code": "Contract nr 2",
                "name": "CON/22/0002",
                "partner_id": self.partner.id,
            }
        )
        contract_2.flush()
        copy_contract_2 = contract_2.copy()
        self.assertTrue(copy_contract_2.name[:11] != contract_2.name)

    def test_pre_init_hook(self):
        contract_3 = self.contract_contract.create(
            {
                "code": "Contract nr 3",
                "name": "CON/22/0003",
                "partner_id": self.partner.id,
            }
        )
        self.cr.execute(
            "update contract_contract set name='/' where id=%s",
            (tuple(contract_3.ids),),
        )
        contract_3.invalidate_cache()
        self.assertEqual(contract_3.name, "/")
        pre_init_hook(self.cr)
        contract_3.invalidate_cache()
        self.assertEqual(contract_3.name, "!!mig!!{}".format(contract_3.id))
