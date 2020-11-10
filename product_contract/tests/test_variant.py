# Copyright 2020 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

PCTI = "property_contract_template_id"


class TestProductVariant(TransactionCase):
    def setUp(self):
        super(TestProductVariant, self).setUp()
        self.contract = self.env["contract.template"].create({"name": "Test"})
        self.attribute = self.env["product.attribute"].create({"name": "Brol"})
        atid = self.attribute.id
        pav = self.env["product.attribute.value"]
        self.attr_value_plic = pav.create({"name": "Plic", "attribute_id": atid})
        self.attr_value_ploc = pav.create({"name": "Ploc", "attribute_id": atid})
        atvids = [self.attr_value_plic.id, self.attr_value_ploc.id]
        self.product_template = self.env["product.template"].create(
            {
                "name": "Potiquet",
                "type": "service",
                "is_contract": True,
                PCTI: self.contract.id,
                "attribute_line_ids": [
                    (0, 0, {"attribute_id": atid, "value_ids": [(6, 0, atvids)]})
                ],
            }
        )

    def test_change_contract_on_variants(self):
        """The contract on variant should be the one on the template, unless
           manually changed.
        """
        contract_plic = self.env["contract.template"].create({"name": "Plic"})
        contract_ploc = self.env["contract.template"].create({"name": "Ploc"})
        template = self.product_template
        plic, ploc = self.product_template.product_variant_ids

        for variant in self.product_template.product_variant_ids:
            self.assertEqual(variant[PCTI], template[PCTI])

        # editing a variant only edits the variant itself
        plic[PCTI] = contract_plic
        self.assertEqual(plic[PCTI], contract_plic)
        self.assertEqual(template[PCTI], self.contract)
        self.assertEqual(ploc[PCTI], self.contract)

        # editing the template only edits the variants that have the default contract
        template[PCTI] = contract_ploc
        self.assertEqual(plic[PCTI], contract_plic)
        self.assertEqual(template[PCTI], contract_ploc)
        self.assertEqual(ploc[PCTI], contract_ploc)

        # removing the template contract does not impact the variants
        template[PCTI] = False
        self.assertEqual(plic[PCTI], contract_plic)
        self.assertTrue(not template[PCTI])
        self.assertEqual(ploc[PCTI], contract_ploc)

    def test_change_is_contract(self):
        """If we remove the contract, it should be removed from the variants."""
        self.product_template.is_contract = False
        self.assertTrue(not self.product_template.product_variant_ids.mapped(PCTI))

    def test_check_contract_template(self):
        """It should not be possible to have products with a contract template
           if they aren't contracts.
        """
        values = {"name": "Test", "is_contract": False}
        not_a_contract = self.env["product.template"].create(values)

        variant = not_a_contract.product_variant_ids
        with self.assertRaises(ValidationError):
            variant[PCTI] = self.contract

        values["property_contract_template_id"] = self.contract.id
        with self.assertRaises(ValidationError):
            self.env["product.product"].create(values)

    def test_check_is_contract(self):
        """If we activate the constrain_contract_products settings, it is not possible
           to create/write variants without setting a contract template.
        """
        company = self.env["res.company"]._company_default_get()
        company.constrain_contract_products = False
        values = {"type": "service", "is_contract": True}

        product = self.env["product.product"].create(dict(**values, name="not"))
        self.assertTrue(product.is_contract)

        plic = self.product_template.product_variant_ids[0]
        ploc = self.product_template.product_variant_ids[1]

        plic.write({PCTI: False})
        self.assertTrue(plic.is_contract)
        self.assertTrue(not plic[PCTI])

        company.constrain_contract_products = True
        with self.assertRaises(ValidationError):
            self.env["product.product"].create(dict(**values, name="new"))

        with self.assertRaises(ValidationError):
            ploc.write({PCTI: False})
