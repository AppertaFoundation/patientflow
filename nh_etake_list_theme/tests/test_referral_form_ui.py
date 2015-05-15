from openerp.osv import osv

import openerp.tests

class TestReferralFormUI(openerp.tests.SingleTransactionCase, openerp.tests.HttpCase):

    """
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
    """
    def test_receptionist_able_to_update_patient_arrival(self):
        api = self.registry['nh.eobs.api']
        group_pool = self.registry['res.groups']
        user_pool = self.registry['res.users']
        patient_pool = self.registry['nh.clinical.patient']
        patient_flow_pool = self.registry['nh.etake_list.overview']
        cr, uid = self.cr, self.uid

        adtgroup_id = group_pool.search(cr, uid, [['name', '=', 'NH Clinical ADT Group']])
        adtuid_ids = user_pool.search(cr, uid, [['groups_id', 'in', adtgroup_id]])

        if not adtuid_ids:
            raise osv.except_osv('No ADT User!', 'ADT user required to register patient.')

        other_identifier = '12345'
        patient = {
            'patient_identifier': '4546',
            'family_name': 'will',
            'middle_names': 'A',
            'given_name': 'E',
            'dob': '14/05/2015',
            'gender': 'M',
            'sex': 'F',
            'ethnicity': 'A'
        }
        pt_id = api.register(cr, adtuid_ids[0], other_identifier, patient)
        api.admit(cr, adtuid_ids[0], other_identifier, {'location': 'WEAU'})

        self.phantom_js("/web",
            "openerp.Tour.run('junior_doctor_able_to_create_diagnosis_plans_tasks', 'test')",
            "openerp.Tour.tours.junior_doctor_able_to_create_diagnosis_plans_tasks", login="robert", inject=[['Test Script', 'http://localhost:8069/nh_etake_list_theme/static/src/gui_test/feature_steps.js']]
        )

        meh = patient_flow_pool.search(cr, uid, [['hospital_number', '=', other_identifier]])
        meheh = patient_flow_pool.read(cr, uid, meh, [])

    """
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
    def test_registrar_able_to_create_referrals(self):
        self.phantom_js("/web",
            "openerp.Tour.run('registrar_able_to_create_referrals', 'test')",
            "openerp.Tour.tours.registrar_able_to_create_referrals", login="roger"
        )
    """


