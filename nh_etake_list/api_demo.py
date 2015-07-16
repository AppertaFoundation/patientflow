from openerp.osv import orm
import logging
_logger = logging.getLogger(__name__)

from faker import Faker
fake = Faker()

class nh_clinical_api_demo(orm.AbstractModel):
    _name = 'nh.clinical.api.demo'
    _inherit = 'nh.clinical.api.demo'

    def build_unit_test_env2(self, cr, uid, wards=None, bed_count=2, patient_count=2, context=False, users=None):
        """
        Create a default unit test environment for basic unit tests.
            2 WARDS - U and T
            2 beds per ward - U01, U02, T01, T02
            2 patients admitted per ward
            1 patient placed in bed per ward
        The environment is customizable, the wards parameter must be a list of ward codes. All the other parameters are
        the number of beds, patients and placements we want.

        users parameter expects a dictionary with the following format:
            {
                'receptionists': {
                    'name': ['login', 'ward_code']
                },
                'junior_doctors': {
                    'name': ['login', [list of locations]]
                },
                'registrars': {
                    'name': ['login', [list of locations]]
                },
                'consultants': {
                    'name': ['login', [list of locations]]
                }
            }
            if there is no data the default behaviour will be to add a receptionist per ward i.e. 'RU' and 'RT' and
            a junior doctor and consultant responsible for all beds in the ward i.e. 'JDU' and 'JDT' / 'CU' and 'CT'
        """
        activity_pool = self.pool['nh.activity']
        context_pool = self.pool['nh.clinical.context']

        if not wards:
            wards = ['U', 'T']
        location_pool = self.pool['nh.clinical.location']
        pos_id = self.create(cr, uid, 'nh.clinical.pos')
        pos_location_id = location_pool.search(cr, uid, [('pos_id', '=', pos_id)])[0]

        adt_uid = self.create(cr, uid, 'res.users', 'user_adt', {'pos_id': pos_id})

        if context:
            context_ids = context_pool.search(cr, uid, [['name', '=', context]])
            context = [[6, False, context_ids]] if context_ids else False

        # LOCATIONS
        ward_ids = [self.create(cr, uid, 'nh.clinical.location', 'location_ward', {'context_ids': context, 'parent_id': pos_location_id, 'name': 'Ward '+w, 'code': w}) for w in wards]
        i = 0
        bed_ids = {}
        bed_codes = {}
        for wid in ward_ids:
            bed_ids[wards[i]] = [self.create(cr, uid, 'nh.clinical.location', 'location_bed', {'context_ids': context, 'parent_id': wid, 'name': 'Bed '+str(n), 'code': wards[i]+str(n)}) for n in range(bed_count)]
            bed_codes[wards[i]] = [wards[i]+str(n) for n in range(bed_count)]
            i += 1

        # USERS
        if not users:
            users = {'receptionists': {}, 'junior_doctors': {}, 'consultants': {}}
            for w in wards:
                users['receptionists']['R'+w] = ['R'+w, w]
                users['junior_doctors']['JD'+w] = ['JD'+w, bed_codes[w]]
                users['consultants']['C'+w] = ['C'+w, bed_codes[w]]

        if users.get('receptionists'):
            r_ids = {}
            for r in users['receptionists'].keys():
                wid = location_pool.search(cr, uid, [('code', '=', users['receptionists'][r][1])])
                r_ids[r] = self.create(cr, uid, 'res.users', 'user_receptionist', {'name': r, 'login': users['receptionists'][r][0], 'location_ids': [[6, False, wid]], 'pos_id': pos_id})

        if users.get('junior_doctors'):
            jd_ids = {}
            for jd in users['junior_doctors'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['junior_doctors'][jd][1])])
                jd_ids[jd] = self.create(cr, uid, 'res.users', 'user_junior_doctor', {'name': jd, 'login': users['junior_doctors'][jd][0], 'location_ids': [[6, False, lids]], 'pos_id': pos_id})

        if users.get('registrars'):
            r_ids = {}
            for r in users['registrars'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['registrars'][r][1])])
                r_ids[r] = self.create(cr, uid, 'res.users', 'user_registrar', {'name': r, 'login': users['registrars'][r][0], 'location_ids': [[6, False, lids]], 'pos_id': pos_id})

        if users.get('consultants'):
            c_ids = {}
            for c in users['consultants'].keys():
                lids = location_pool.search(cr, uid, [('code', 'in', users['consultants'][c][1])])
                c_ids[c] = self.create(cr, uid, 'res.users', 'user_consultant', {'name': c, 'login': users['consultants'][c][0], 'location_ids': [[6, False, lids]], 'pos_id': pos_id})

        if users.get('referral_team'):
            rt_ids = {}
            for rt in users['referral_team'].keys():
                rt_ids[rt] = self.create(cr, uid, 'res.users', 'user_referral_team', {'name': rt, 'login': users['referral_team'][rt], 'pos_id': pos_id})

        self.create(cr, uid, 'res.users', 'user_adt', {'name': 'ADT', 'login': 'unittestadt', 'pos_id': pos_id})

        patient_ids = []
        for wcode in wards:
            activity_pool = self.pool['nh.activity']
            adt_register_pool = self.pool['nh.clinical.adt.patient.register']
            adt_admit_pool = self.pool['nh.clinical.adt.patient.admit']
            reg_activity_ids = [adt_register_pool.create_activity(cr, adt_uid, {},
                                                                  {'other_identifier': 'hn_'+wcode+str(i)})
                                for i in range(patient_count)]
            [activity_pool.complete(cr, adt_uid, id) for id in reg_activity_ids]
            admit_activity_ids = [adt_admit_pool.create_activity(cr, adt_uid, {},
                                                                 {'other_identifier': 'hn_'+wcode+str(i),
                                                                  'location': wcode})
                                  for i in range(patient_count)]
            [activity_pool.complete(cr, adt_uid, id) for id in admit_activity_ids]
            patient_ids += [aa.patient_id.id for aa in activity_pool.browse(cr, uid, admit_activity_ids)]

        return patient_ids