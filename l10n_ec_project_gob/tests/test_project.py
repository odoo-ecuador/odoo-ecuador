from openerp.tests.common import TransactionCase

class ProjectTest(TransactionCase):

    def setUp(self):
        super(ProjectTest, self).setUp()
        self.project_model = self.registry('project.project')


