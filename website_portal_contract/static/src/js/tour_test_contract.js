/* Copyright 2017 Laslabs Inc.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('website_portal_contract.tour_test_contract', function(require) {
    'use strict';

    var base = require('web_editor.base');
    var _t = require('web.core')._t;
    var tour = require('web_tour.tour');

    tour.register(
        'test_contract_view',
        {
            test: true,
            url: '/my/home',
            name: 'Test website portal contract view',
            wait_for: base.ready()
        },
        [
            {
                content: _t('Click on Your Contracts'),
                trigger: "a:contains('Your Contracts')"
            },
            {
                content: _t('Click on Demo Project'),
                trigger: "a:contains('Demo Contract - Demo Portal User')"
            },
            {
                content: _t('Click History'),
                trigger: "a:contains('History')"
            }
        ]
    );

    return {};

});
