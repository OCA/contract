from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                tracking_disable=True,
                no_reset_password=True,
            )
        )
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.product1 = cls.env.ref("product.product_product_1")
        cls.product2 = cls.env.ref("product.product_product_2")
        cls.sale = cls.env.ref("sale.sale_order_2")
        cls.contract_template1 = cls.env["contract.template"].create(
            {"name": "Template 1"}
        )
        cls.contract_template2 = cls.env["contract.template"].create(
            {
                "name": "Template 2",
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product2.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": cls.product2.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "yearly",
                            "recurring_interval": 1,
                        },
                    )
                ],
            }
        )
        cls.product1.with_company(cls.sale.company_id).write(
            {
                "is_contract": True,
                "recurrence_number": 12,
                "recurring_rule_type": "monthlylastday",
                "recurring_invoicing_type": "post-paid",
                "property_contract_template_id": cls.contract_template1.id,
            }
        )
        cls.product2.with_company(cls.sale.company_id).write(
            {
                "is_contract": True,
                "property_contract_template_id": cls.contract_template2.id,
            }
        )
        cls.order_line1 = cls.sale.order_line.filtered(
            lambda line: line.product_id == cls.product1
        )
        cls.order_line1.date_start = "2018-01-01"
        cls.order_line1.recurrence_number = 12
        pricelist = cls.sale.partner_id.property_product_pricelist.id
        cls.contract = cls.env["contract.contract"].create(
            {
                "name": "Test Contract 2",
                "partner_id": cls.sale.partner_id.id,
                "pricelist_id": pricelist,
                "contract_type": "sale",
                "line_recurrence": True,
                "contract_template_id": cls.contract_template1.id,
                "contract_line_ids": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product1.id,
                            "name": "Services from #START# to #END#",
                            "quantity": 1,
                            "uom_id": cls.product1.uom_id.id,
                            "price_unit": 100,
                            "discount": 50,
                            "recurring_rule_type": "monthly",
                            "recurring_interval": 1,
                            "date_start": "2016-02-15",
                            "recurring_next_date": "2016-02-29",
                        },
                    )
                ],
            }
        )
        cls.contract_line = cls.contract.contract_line_ids[0]
        cls.sale.order_line._compute_product_contract_data()

    def test_contract_upsell_3(self):
        self.contract_line.termination_notice_interval = True
        self.contract_line.termination_notice_rule_type = True
        self.contract_line.automatic_price = True
        self.contract_line.manual_renew_needed = True
        self.assertFalse(self.contract_line.termination_notice_interval)
        self.assertFalse(self.contract_line.termination_notice_rule_type)
        self.assertFalse(self.contract_line.automatic_price)
        self.assertFalse(self.contract_line.manual_renew_needed)

    def test_onchange_product_id_termination_info(self):
        self.product2.write(
            {
                "termination_notice_interval": "6",
                "termination_notice_rule_type": "weekly",
                "automatic_price": True,
                "manual_renew_needed": True,
            }
        )
        self.assertEqual(self.contract_line.termination_notice_interval, 6)
        self.assertEqual(self.contract_line.termination_notice_rule_type, "weekly")
        self.assertEqual(self.contract_line.automatic_price, True)
        self.assertEqual(self.contract_line.manual_renew_needed, True)

    def test_check_contact_is_not_terminated(self):
        self.contract.is_terminated = True
        with self.assertRaises(ValidationError):
            self.order_line1.contract_id = self.contract

    def test_check_contact_is_not_terminated_1(self):
        self.order_line1.contract_id = self.contract
        self.sale.action_confirm()
        self.contract.is_terminated = True
        self.sale._action_cancel()
        with self.assertRaises(ValidationError):
            self.sale.action_draft()
        self.contract.is_terminated = False
        self.sale.action_draft()




