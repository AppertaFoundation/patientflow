__author__ = 'neova'

import openerp.tests

class TestReferralFormUI(openerp.tests.HttpCase):

    def test_referral_nurse_able_to_create_referral(self):
        self.phantom_js("/web",
            "openerp.Tour.run('referral_nurse_able_to_create_referral', 'test')",
            "openerp.Tour.tours.referral_nurse_able_to_create_referral", login="taylor"
        )
    def test_referral_nurse_able_to_update_patient_arrival(self):
        self.phantom_js("/web",
            "openerp.Tour.run('referral_nurse_able_to_update_patient_arrival', 'test')",
            "openerp.Tour.tours.referral_nurse_able_to_update_patient_arrival", login="taylor"
        )
    def test_(self):
        self.phantom_js("/web",
            "openerp.Tour.run('receptionist_able_to_update_patient_arrival', 'test')",
            "openerp.Tour.tours.receptionist_able_to_update_patient_arrival", login="robert"
        )




