/* Copyright 2017 Laslabs Inc.
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

odoo.define('website_portal_contract.tour_test_contract', function(require) {
    'use strict';

    var tour = require('web_tour.tour');
    var base = require('web_editor.base');
    var website = require('website.website');

    tour.register(
        'test_contract_view',
        {
            url: '/my/home',
            name: 'Test website portal contract view',
            test: true
        },
        [
            {
                content: 'Click on Your Contracts',
                trigger: "a:contains('Your Contracts')"
            },
            {
                content: 'Click on Demo Project',
                trigger: "a:contains('Demo Contract - Demo Portal User')"
            },
            {
                content: 'Click History',
                trigger: "a:contains('History')"
            }
        ]
    );

    return {};

});
