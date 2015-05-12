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
    def test_receptionist_able_to_update_patient_arrival(self):
        self.phantom_js("/web",
            "openerp.Tour.run('receptionist_able_to_update_patient_arrival', 'test')",
            "openerp.Tour.tours.receptionist_able_to_update_patient_arrival", login="robert"
        )
    def test_junior_doctor_able_to_update_patient_clerking_in_progress_stage(self):
        self.phantom_js("/web",
            "openerp.Tour.run('junior_doctor_able_to_update_patient_clerking_in_progress_stage', 'test')",
            "openerp.Tour.tours.junior_doctor_able_to_update_patient_clerking_in_progress_stage", login="james"
        )

    def test_junior_doctor_able_to_create_diagnosis_plans_tasks(self):
        self.phantom_js("/web",
            "openerp.Tour.run('junior_doctor_able_to_create_diagnosis_plans_tasks', 'test')",
            "openerp.Tour.tours.junior_doctor_able_to_create_diagnosis_plans_tasks", login="james"
        )
    def test_junior_doctor_able_to_update_patient_arrival(self):
        self.phantom_js("/web",
            "openerp.Tour.run('junior_doctor_able_to_update_patient_arrival', 'test')",
            "openerp.Tour.tours.junior_doctor_able_to_update_patient_arrival", login="james"
        )



