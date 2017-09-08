# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import HttpCase


class TestAccountAnalyticContractTemplate(HttpCase):

    def setUp(self):
        super(TestAccountAnalyticContractTemplate, self).setUp()
        self.template = self.env.ref(
            'website_portal_contract.website_contract_template_default'
        )

    def test_open_template(self):
        """ Test open_template returns correct url """
        self.assertEquals(
            self.template.open_template()['url'],
            '/contract/template/%d' % self.template.id,
        )
