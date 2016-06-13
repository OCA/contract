# -*- coding: utf-8 -*-
# © 2016 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestContractInvoiceMergeByPartner(TransactionCase):
    """ Use case : Prepare some data for current test case """
    def setUp(self):
        super(TestContractInvoiceMergeByPartner, self).setUp()
