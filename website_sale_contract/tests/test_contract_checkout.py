# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from .setup import Setup


class TestContractCheckout(Setup):

    def test_build_contract_checkout(self):
        """ It should properly create doubly linked list """
        checkout = self._build_test_contract_checkout()
        self.assertEquals(
            len(checkout.temp_contract_ids), 3,
        )
        for index, contract in enumerate(checkout.temp_contract_ids):
            if index != 0:
                self.assertEquals(
                    contract.previous_contract_id,
                    checkout.temp_contract_ids[index - 1],
                )
            if index != 2:
                self.assertEquals(
                    contract.next_contract_id,
                    checkout.temp_contract_ids[index + 1],
                )
