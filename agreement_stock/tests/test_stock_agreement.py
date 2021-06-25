# Copyright (C) 2021 Open Source Integrators
# Copyright (C) 2021 Serpent Consulting Services
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests import common


class TestStockAgreement(common.TransactionCase):
    def test_stockagreement(self):
        agreement_1 = self._create_agreement()
        partner_1 = self.env["res.partner"].create({"name": "TestPartner1"})
        product_1 = self.env["product.product"].search(
            [("type", "=", "product")], limit=1
        )
        picking_1 = self.env["stock.picking"].create(
            {
                "partner_id": partner_1.id,
                "picking_type_id": self.env.ref("stock.picking_type_out").id,
                "location_id": self.env.ref("stock.stock_location_stock").id,
                "location_dest_id": self.env.ref("stock.stock_location_customers").id,
                "agreement_id": agreement_1.id,
            }
        )
        self.env["stock.move"].create(
            {
                "product_id": product_1.id,
                "name": product_1.partner_ref,
                "product_uom_qty": 5,
                "quantity_done": 5,
                "picking_id": picking_1.id,
                "product_uom": product_1.uom_id.id,
                "location_id": picking_1.location_id.id,
                "location_dest_id": picking_1.location_dest_id.id,
            }
        )
        agreement_1._compute_picking_count()
        agreement_1._compute_move_count()
        agreement_1._compute_lot_count()

        self.assertEqual(agreement_1.picking_count, 1)
        self.assertEqual(agreement_1.move_count, 1)
        self.assertEqual(agreement_1.lot_count, 0)

    def _create_agreement(self):
        agreement = self.env["agreement"].create(
            {
                "code": "DA",
                "name": "Demo Agreement",
            }
        )
        return agreement
