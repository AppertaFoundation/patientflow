__author__ = 'neova'

import openerp.tests

class TestReferralFormUI(openerp.tests.HttpCase):

    def test_referral_form_creation(self):
        self.phantom_js("/web",
            "openerp.Tour.run('tour_test', 'test')",
            "openerp.Tour.tours.tour_test", login="caroline"
        )
