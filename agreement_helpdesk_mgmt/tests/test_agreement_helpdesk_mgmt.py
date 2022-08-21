# Copyright (C) 2020 - TODAY, Marcel Savegnago - Escodoo
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import odoo.tests.common as common


class TestAgreementHelpdeskMgmt(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAgreementHelpdeskMgmt, cls).setUpClass()
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'email': 'test@test.com',
        })
        cls.agreement = cls.env['agreement'].create({
            'name': 'Test Agreement',
            'partner_id': cls.partner.id,
        })
        cls.ticket = cls.env['helpdesk.ticket'].create({
            'name': 'Test Helpdesk Ticket',
            'description': 'Test Helpdesk Ticket',
            'partner_id': cls.partner.id,
            'agreement_id': cls.agreement.id,
        })

    def test_compute_ticket_count(self):
        self.agreement._compute_ticket_count()
        self.assertEqual(
            self.agreement.ticket_count, 1)

    def test_action_view_ticket(self):
        result = self.agreement.action_view_ticket()
        self.assertEqual(result['res_id'], self.ticket.id)
