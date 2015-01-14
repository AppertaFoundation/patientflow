from openerp.tests import common

import logging
_logger = logging.getLogger(__name__)

from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from faker import Faker
fake = Faker()
seed = fake.random_int(min=0, max=9999999)


def next_seed():
    global seed
    seed += 1
    return seed


class test_shift_management(common.SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(test_shift_management, cls).setUpClass()
        cr, uid = cls.cr, cls.uid

        cls.users_pool = cls.registry('res.users')
        cls.groups_pool = cls.registry('res.groups')
        cls.partner_pool = cls.registry('res.partner')
        cls.activity_pool = cls.registry('nh.activity')
        cls.patient_pool = cls.registry('nh.clinical.patient')
        cls.location_pool = cls.registry('nh.clinical.location')
        cls.pos_pool = cls.registry('nh.clinical.pos')
        cls.spell_pool = cls.registry('nh.clinical.spell')
        cls.api_pool = cls.registry('nh.clinical.api')

        # SHIFT MANAGEMENT DATA MODELS
        cls.pattern_pool = cls.registry('nh.clinical.shift.pattern')
        cls.shift_pool = cls.registry('nh.clinical.shift')
        cls.timespan_pool = cls.registry('nh.clinical.spell.timespan')


        cls.apidemo = cls.registry('nh.clinical.api.demo')

        cls.apidemo.build_unit_test_env(cr, uid, bed_count=4, patient_placement_count=2)

        cls.wu_id = cls.location_pool.search(cr, uid, [('code', '=', 'U')])[0]
        cls.wt_id = cls.location_pool.search(cr, uid, [('code', '=', 'T')])[0]
        cls.pos_id = cls.location_pool.read(cr, uid, cls.wu_id, ['pos_id'])['pos_id'][0]
        cls.pos_location_id = cls.pos_pool.read(cr, uid, cls.pos_id, ['location_id'])['location_id'][0]

        cls.wmu_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMU')])[0]
        cls.wmt_id = cls.users_pool.search(cr, uid, [('login', '=', 'WMT')])[0]
        cls.nu_id = cls.users_pool.search(cr, uid, [('login', '=', 'NU')])[0]
        cls.nt_id = cls.users_pool.search(cr, uid, [('login', '=', 'NT')])[0]
        cls.adt_id = cls.users_pool.search(cr, uid, [('groups_id.name', 'in', ['NH Clinical ADT Group']), ('pos_id', '=', cls.pos_id)])[0]

    def test_shifts_and_patterns(self):
        cr, uid = self.cr, self.uid

        pattern_u_1_id = self.pattern_pool.create(cr, uid, {'start_time_string': '08:00', 'end_time_string': '20:00', 'location_id': self.wu_id})
        pattern_u_2_id = self.pattern_pool.create(cr, uid, {'start_time_string': '20:00', 'end_time_string': '08:00', 'location_id': self.wu_id})
        try:
            pattern_u_3_id = self.pattern_pool.create(cr, uid, {'start_time_string': '06:00', 'end_time_string': '07:00', 'location_id': self.wu_id})
        except:
            pattern_u_3_id = False
            _logger.debug('Overlapping shift pattern exception raised correctly')
        self.assertFalse(pattern_u_3_id, msg='Overlapping shift patterns allowed')

        datetime_test = [
            [dt(year=2015, month=1, day=1, hour=8, minute=0, second=0), 0, 0, pattern_u_1_id, pattern_u_2_id],
            [dt(year=2015, month=1, day=1, hour=8, minute=30, second=0), 0, 30, pattern_u_1_id, pattern_u_2_id],
            [dt(year=2015, month=1, day=1, hour=21, minute=0, second=0), 60, 0, pattern_u_2_id, pattern_u_1_id],
            [dt(year=2015, month=1, day=1, hour=0, minute=0, second=0), 240, 0, pattern_u_2_id, pattern_u_1_id],
            [dt(year=2015, month=1, day=1, hour=20, minute=0, second=0), 0, 0, pattern_u_2_id, pattern_u_1_id]
        ]

        for dtt in datetime_test:
            self.assertTrue(self.pattern_pool.distance(cr, uid, pattern_u_1_id, dtt[0]) == dtt[1], msg='Distance not correct')
            self.assertTrue(self.pattern_pool.distance(cr, uid, pattern_u_2_id, dtt[0]) == dtt[2], msg='Distance not correct')

        for dtt in datetime_test:
            self.assertTrue(self.pattern_pool.closest_pattern(cr, uid, self.wu_id, datetime=dtt[0]) == dtt[3], msg='Closest pattern not correct')
            self.assertTrue(self.pattern_pool.next_pattern(cr, uid, self.wu_id, datetime=dtt[0]) == dtt[4], msg='Next pattern not correct')

        self.shift_pool.generate_all_shifts(cr, uid)

        current_shift = self.shift_pool.current_shift(cr, uid, self.wu_id)
        next_shift = self.shift_pool.next_shift(cr, uid, self.wu_id)
        self.assertTrue(current_shift, msg='Current shift not created')
        self.assertTrue(next_shift, msg='Next shift not created')
        self.assertFalse(self.shift_pool.last_shift(cr, uid, self.wu_id), msg='Last shift returned but should not exist')
        self.assertFalse(self.shift_pool.previous_shift(cr, uid, self.wu_id), msg='Previous shift returned but should not exist')

        current_shift = self.shift_pool.browse(cr, uid, current_shift)
        next_shift = self.shift_pool.browse(cr, uid, next_shift)
        self.assertTrue(current_shift.position == '1', msg='Positions not updated correctly: %s' % current_shift.position)
        self.assertTrue(next_shift.position == '0', msg='Positions not updated correctly: %s' % next_shift.position)



