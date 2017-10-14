# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import HttpCase
from odoo.addons.website.models.website import slug


class TestController(HttpCase):

    post_install = True
    at_install = False

    def test_template_view(self):
        """ It should respond with 200 status """
        contract = self.env.ref(
            'website_portal_contract.'
            'website_contract_template_default'
        )
        self.authenticate('admin', 'admin')
        response = self.url_open(
            '/contract/template/%s' % slug(contract)
        )
        self.assertEquals(
            response.getcode(),
            200,
        )
