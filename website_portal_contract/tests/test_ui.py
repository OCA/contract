# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import HttpCase


class TestController(HttpCase):

    post_install = True
    at_install = False

    def test_portal_contract_view_tour(self):
        """ Tests contract view is correct """
        tour = "odoo.__DEBUG__.services['web_tour.tour']"
        self.phantom_js(
            url_path='/my/home',
            code="%s.run('test_contract_view')" % tour,
            ready="%s.tours.test_contract_view.ready" % tour,
            login='portal',
        )
