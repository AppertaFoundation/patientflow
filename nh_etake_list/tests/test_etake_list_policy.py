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


class TestETakeListPolicy(common.SingleTransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestETakeListPolicy, cls).setUpClass()
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

        cls.patient_ids = cls.apidemo.build_unit_test_env2(cr, uid, context='etakelist')

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

    def test_etake_list_policy_triggers(self):
        cr, uid = self.cr, self.uid

        patient_id = fake.random_element(self.patient_ids)
        spell_ids = self.activity_pool.search(cr, uid, [['data_model', '=', 'nh.clinical.spell'], ['patient_id', '=', patient_id]])
        self.assertTrue(spell_ids, msg="Test set up Failed. No spell found for the patient")
        spell_activity = self.activity_pool.browse(cr, uid, spell_ids[0])
        user_ids = False
        if self.ru_id in [user.id for user in spell_activity.user_ids]:
            user_ids = {'receptionist': self.ru_id, 'junior': self.jdu_id, 'consultant': self.cu_id}
        else:
            user_ids = {'receptionist': self.rt_id, 'junior': self.jdt_id, 'consultant': self.ct_id}

        # Patient Referral
        referral_activity_ids = self.activity_pool.search(cr, uid, [['state', 'not in', ['completed', 'cancelled']], ['patient_id', '=', patient_id], ['data_model', '=', 'nh.clinical.patient.referral']])
        self.assertTrue(referral_activity_ids, msg="Referral activity not triggered after admission")
        self.assertTrue(len(referral_activity_ids) == 1, msg="There is more than one referral activity for the same patient!")
        # Complete Referral
        self.activity_pool.complete(cr, user_ids['receptionist'], referral_activity_ids[0])
        referral_activity_data = self.activity_pool.read(cr, uid, referral_activity_ids[0], ['date_terminated', 'state', 'terminate_uid'])
        self.assertTrue(referral_activity_data['state'] == 'completed', msg="Referral Completed: State not updated correctly.")
        self.assertTrue(referral_activity_data['date_terminated'], msg="Referral Completed: Date terminated not registered.")
        self.assertTrue(referral_activity_data['terminate_uid'][0] == user_ids['receptionist'], msg="Referral Completed: Completed by (user) not registered correctly.")

        # Patient Clerking
        clerking_activity_ids = self.activity_pool.search(cr, uid, [['state', 'not in', ['completed', 'cancelled']], ['patient_id', '=', patient_id], ['data_model', '=', 'nh.clinical.patient.clerking']])
        self.assertTrue(clerking_activity_ids, msg="Clerking activity not triggered after referral")
        self.assertTrue(len(clerking_activity_ids) == 1, msg="There is more than one clerking activity for the same patient!")
        # Complete Clerking
        self.activity_pool.complete(cr, user_ids['junior'], clerking_activity_ids[0])
        clerking_activity_data = self.activity_pool.read(cr, uid, clerking_activity_ids[0], ['date_terminated', 'state', 'terminate_uid'])
        self.assertTrue(clerking_activity_data['state'] == 'completed', msg="Clerking Completed: State not updated correctly.")
        self.assertTrue(clerking_activity_data['date_terminated'], msg="Clerking Completed: Date terminated not registered.")
        self.assertTrue(clerking_activity_data['terminate_uid'][0] == user_ids['junior'], msg="Clerking Completed: Completed by (user) not registered correctly.")

        # Patient Review
        review_activity_ids = self.activity_pool.search(cr, uid, [['state', 'not in', ['completed', 'cancelled']], ['patient_id', '=', patient_id], ['data_model', '=', 'nh.clinical.patient.review']])
        self.assertTrue(review_activity_ids, msg="Review activity not triggered after clerking")
        self.assertTrue(len(review_activity_ids) == 1, msg="There is more than one review activity for the same patient!")
        # Complete Review
        self.activity_pool.complete(cr, user_ids['consultant'], review_activity_ids[0])
        review_activity_data = self.activity_pool.read(cr, uid, review_activity_ids[0], ['date_terminated', 'state', 'terminate_uid'])
        self.assertTrue(review_activity_data['state'] == 'completed', msg="Review Completed: State not updated correctly.")
        self.assertTrue(review_activity_data['date_terminated'], msg="Review Completed: Date terminated not registered.")
        self.assertTrue(review_activity_data['terminate_uid'][0] == user_ids['consultant'], msg="Review Completed: Completed by (user) not registered correctly.")