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
        cls.form_pool = cls.registry('nh.clinical.patient.referral.form')
        cls.tci_pool = cls.registry('nh.clinical.patient.tci')

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
        cls.regu_id = cls.users_pool.search(cr, uid, [('login', '=', 'REGU')])[0] #Registrar on ward U
        cls.regt_id = cls.users_pool.search(cr, uid, [('login', '=', 'REGT')])[0] #Registrar on ward T
        cls.refteam_id = cls.users_pool.search(cr, uid, [('login', '=', 'RT1')])[0] #Referral Team User
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

    def test_referral_form(self):
        cr, uid = self.cr, self.uid
        # Submit an empty form
        form_id = self.form_pool.create(cr, self.refteam_id, {})
        self.assertTrue(form_id, msg="Referral form not created")
        form = self.form_pool.browse(cr, uid, form_id)
        self.assertTrue(form.source == 'gp', msg="Referral form created: incorrect default source")
        self.assertTrue(form.gender == 'NSP', msg="Referral form created: incorrect default gender")
        self.assertTrue(form.ethnicity == 'Z', msg="Referral form created: incorrect default ethnicity")
        self.assertTrue(form.patient_id, msg="Referral form created: patient not created automatically")
        self.assertTrue(form.patient_id.gender == 'NSP', msg="Referral form created: incorrect default patient gender")
        self.assertTrue(form.patient_id.ethnicity == 'Z', msg="Referral form created: incorrect default patient ethnicity")
        self.assertTrue(form.source == 'gp', msg="Referral form created: incorrect default source")
        referral_id = self.referral_pool.search(cr, uid, [['patient_id', '=', form.patient_id.id]])
        self.assertTrue(referral_id, msg="Referral form created: referral activity not triggered")
        referral = self.referral_pool.browse(cr, uid, referral_id[0])
        self.assertTrue(referral.form_id.id == form_id, msg="Referral triggered: referral form not linked correctly")
        # Submit a form for an existing patient
        patient_ids = self.patient_ids
        patient_id = fake.random_element(patient_ids)
        form_data = {
            'patient_id': patient_id,
            'gender': 'U',
            'middle_names': 'John'
        }
        try:
            form_id = self.form_pool.create(cr, self.refteam_id, form_data)
        except Exception as e:
            self.assertTrue(e.args[1].startswith("Cannot submit form. The values in the form do not match the selected patient data"), msg="Unexpected reaction to attempt to create a form with an existing patient (not matching data)!")
        else:
            assert False, "Form successfully created with an existing patient (not matching data)!"
        patient = self.patient_pool.browse(cr, uid, patient_id)
        form_data = {
            'nhs_number': patient.patient_identifier,
            'hospital_number': '0000000001'
        }
        try:
            form_id = self.form_pool.create(cr, self.refteam_id, form_data)
        except Exception as e:
            self.assertTrue(e.args[1].startswith("Cannot submit form. There is already a patient in the system with that NHS number"), msg="Unexpected reaction to attempt to create a form with an existing patient (not matching data)!")
        else:
            assert False, "Form successfully created with an existing patient (not matching data)!"
        form_data = {
            'nhs_number': '0000000001',
            'hospital_number': patient.other_identifier
        }
        try:
            form_id = self.form_pool.create(cr, self.refteam_id, form_data)
        except Exception as e:
            self.assertTrue(e.args[1].startswith("Cannot submit form. There is already a patient in the system with that hospital number"), msg="Unexpected reaction to attempt to create a form with an existing patient (not matching data)!")
        else:
            assert False, "Form successfully created with an existing patient (not matching data)!"

        
    def test_referral(self):
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

        # Patient To Come In
        tci_data = {
            'location_id': self.wu_id,
            'patient_id': patient_id
        }
        tci_activity_id = self.tci_pool.create_activity(cr, uid, {'pos_id': self.pos_id}, {})
        self.activity_pool.submit(cr, self.ru_id, tci_activity_id, tci_data)
        check_tci = self.activity_pool.browse(cr, uid, tci_activity_id)
        
        # test tci activity submitted data
        self.assertTrue(check_tci.data_ref.patient_id.id == patient_id, msg="Patient To Come In: Patient id was not submitted correctly")
        self.assertTrue(check_tci.data_ref.location_id.id == self.wu_id, msg="Patient To Come In: location id was not submitted correctly")
        
        # Complete Patient To Come In
        self.activity_pool.complete(cr, self.ru_id, tci_activity_id)
        check_tci = self.activity_pool.browse(cr, uid, tci_activity_id)
        self.assertTrue(check_tci.state == 'completed', msg="Patient To Come In not completed successfully")
        self.assertTrue(check_tci.date_terminated, msg="Patient To Come In Completed: Date terminated not registered")
        # test spell data
        check_spell = self.activity_pool.browse(cr, uid, spell_activity_id)
        self.assertTrue(check_spell.data_ref.location_id.id == self.wu_id, msg= "Patient To Come In Completed: Spell location not registered correctly")
        # test patient data
        check_patient = self.patient_pool.browse(cr, uid, patient_id)
        self.assertTrue(check_patient.current_location_id.id == self.wu_id, msg= "Patient To Come In Completed: Patient current location not registered correctly")