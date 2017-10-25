# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .setup import Setup


class TestContractTemp(Setup):

    def test_compute_website_url(self):
        """ It should set the correct url """
        contract = self.ContractTemp._convert_line_to_temp_contract(
            self.line_1
        )
        website_url = '/shop/checkout/contract/%d/%s' % (
            contract.id, contract.access_token,
        )
        self.assertEquals(
            contract.website_url,
            website_url,
        )
