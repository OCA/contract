# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Binovo IT Human Project SL <elacunza@binovo.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Contract recurring invoice type monthly - last day",

    'summary': """
        Adds a new invoice recurring period for contracts - month(s) last day.
        """,

    'description': """
        This module allows to create monthly invoices in contracts, on the last day of each month.
    """,

    'author': "Binovo IT Human Project SL",
    'website': "http://www.binovo.es",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales Management',
    'version': '0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account_analytic_analysis'],

    # always loaded
    'data': [
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}