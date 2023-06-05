from odoo.tests import common


class TestAgreement(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @classmethod
    def test_agreement(self):
        self = self.env["agreement"].search([])
        for ag in self:
            ag._compute_task_count()
            count = self.env["project.task"].search_count(
                [("agreement_id", "=", ag.id)]
            )
            ag.task_count = count
