from odoo.tests.common import SavepointCase


class TestAgreement(SavepointCase):
    def test_agreement(self):
        self = self.env["agreement"].search([])
        for ag in self:
            ag._compute_task_count()
            count = self.env["project.task"].search_count(
                [("agreement_id", "=", ag.id)]
            )
            ag.task_count = count
