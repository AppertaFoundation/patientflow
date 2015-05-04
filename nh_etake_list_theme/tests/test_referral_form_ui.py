__author__ = 'neova'

import openerp.tests

class TestReferralFormUI(openerp.tests.HttpCase):

    def test_referral_form_creation(self):
        self.phantom_js("/web",
            "openerp.Tour.run('refferal_nurse_able_to_create_referral', 'test')",
            "openerp.Tour.tours.refferal_nurse_able_to_create_referral", login="caroline"
        )
