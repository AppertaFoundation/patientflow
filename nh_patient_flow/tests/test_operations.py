from openerp.tests import common
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

import logging
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class TestOpsPatientFlow(common.SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestOpsPatientFlow, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        # OPERATIONS DATA MODELS
        cls.referral_pool = cls.registry('nh.clinical.patient.referral')

        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.patient_ids = cls.apidemo.build_unit_test_env2(cr, uid)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.ru_id = cls.users_pool.search(cr, uid, [('login', '=', 'RU')])[0] #Receptionist on ward U
        cls.rt_id = cls.users_pool.search(cr, uid, [('login', '=', 'RT')])[0] #Receptionist on ward T
        cls.jdu_id = cls.users_pool.search(cr, uid, [('login', '=', 'JDU')])[0] #Junior Doctor on ward U
        cls.jdt_id = cls.users_pool.search(cr, uid, [('login', '=', 'JDT')])[0] #Junior Doctor on ward T
        cls.cu_id = cls.users_pool.search(cr, uid, [('login', '=', 'CU')])[0] #Consultant on ward U
        cls.ct_id = cls.users_pool.search(cr, uid, [('login', '=', 'CT')])[0] #Consultant on ward T
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]
        
    def test_Referral(self):
        cr, uid = self.cr, self.uid
        patient_ids = self.patient_ids
        patient_id = fake.random_element(patient_ids)
        code = str(fake.random_int(min=1000001, max=9999999))
        spell_data = {
            'patient_id': patient_id,
            'pos_id': self.pos_id,
            'code': code,
            'start_date': dt.now().strftime(dtf)}
        spell_activity_id = self.spell_pool.create_activity(cr, uid, {}, spell_data)
        self.activity_pool.start(cr, uid, spell_activity_id)

        # Patient Referral
        referral_data = {
            'location_id': self.wu_id,
            'patient_id': patient_id
        }
        referral_activity_id = self.referral_pool.create_activity(cr, uid, {'pos_id': self.pos_id}, {})
        self.activity_pool.submit(cr, self.ru_id, referral_activity_id, referral_data)
        check_referral = self.activity_pool.browse(cr, uid, referral_activity_id)
        
        # test referral activity submitted data
        self.assertTrue(check_referral.data_ref.patient_id.id == patient_id, msg="Patient Referral: Patient id was not submitted correctly")
        self.assertTrue(check_referral.data_ref.location_id.id == self.wu_id, msg="Patient Referral: location id was not submitted correctly")
        
        # Complete Patient Referral
        self.activity_pool.complete(cr, self.ru_id, referral_activity_id)
        check_referral = self.activity_pool.browse(cr, uid, referral_activity_id)
        self.assertTrue(check_referral.state == 'completed', msg="Patient Referral not completed successfully")
        self.assertTrue(check_referral.date_terminated, msg="Patient Referral Completed: Date terminated not registered")
        # test spell data
        check_spell = self.activity_pool.browse(cr, uid, spell_activity_id)
        self.assertTrue(check_spell.data_ref.location_id.id == self.wu_id, msg= "Patient Referral Completed: Spell location not registered correctly")
        # test patient data
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(check_patient.current_location_id.id == self.wu_id, msg= "Patient Referral Completed: Patient current location not registered correctly")