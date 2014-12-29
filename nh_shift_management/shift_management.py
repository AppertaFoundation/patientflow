# -*- coding: utf-8 -*-
from openerp.osv import orm, osv, fields
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
import logging
from openerp import SUPERUSER_ID


_logger = logging.getLogger(__name__)


class nh_clinical_shift_pattern(orm.Model):
    _name = 'nh.clinical.shift.pattern'
    _description = "Location daily shift"

    _columns = {
        'start_time': fields.datetime('Start Time'),
        'start_time_string': fields.char('Start Time', size=5, required=True),
        'end_time': fields.datetime('End Time'),
        'end_time_string': fields.char('End Time', size=5, required=True),
        'duration': fields.integer('Duration (minutes)'),
        'location_id': fields.many2one('nh.clinical.location', 'Location', required=True),
        'active': fields.boolean('Active')
    }

    _defaults = {
        'active': True,
    }

    def distance(self, cr, uid, shift_id, datetime, context=None):
        """Returns the 'distance' in minutes from the datetime since the last shift"""
        if not isinstance(datetime, dt):
            raise osv.except_osv('Error!', 'datetime expected, received %s' % type(datetime))
        shift = self.browse(cr, uid, shift_id, context=context)
        start = dt.strptime(shift.start_time, dtf)
        end = dt.strptime(shift.end_time, dtf)
        if start.hour == end.hour:
            if start.minute == end.minute:
                return 0
            else:
                if datetime.hour < end.hour:
                    return 24*60 - (end.hour*60 + end.minute) + datetime.hour*60 + datetime.minute
                elif datetime.hour > end.hour:
                    return datetime.hour*60 + datetime.minute - (end.hour*60 + end.minute)
                elif end.minute >= datetime.minute >= start.minute:
                    return 0
                elif datetime.minute < end.minute:
                    return 24*60 - (end.hour*60 + end.minute) + datetime.hour*60 + datetime.minute
                return datetime.minute - end.minute
        elif end.hour > start.hour:
            if end.hour >= datetime.hour >= start.hour:
                if datetime.hour == start.hour:
                    return 0 if datetime.minute >= start.minute else 24*60 - (end.hour*60 + end.minute) + datetime.hour*60 + datetime.minute
                elif datetime.hour == end.hour:
                    return 0 if datetime.minute <= end.minute else datetime.minute - end.minute
                else:
                    return 0
            if datetime.hour < end.hour:
                return 24*60 - (end.hour*60 + end.minute) + datetime.hour*60 + datetime.minute
            else:
                return datetime.hour*60 + datetime.minute - (end.hour*60 + end.minute)
        else:
            if datetime.hour >= start.hour or datetime.hour <= end.hour:
                if datetime.hour == start.hour:
                    return 0 if datetime.minute >= start.minute else 24*60 - (end.hour*60 + end.minute) + datetime.hour*60 + datetime.minute
                elif datetime.hour == end.hour:
                    return 0 if datetime.minute <= end.minute else datetime.minute - end.minute
                else:
                    return 0
            if datetime.hour < end.hour:
                return 24*60 - (end.hour*60 + end.minute) + datetime.hour*60 + datetime.minute
            else:
                return datetime.hour*60 + datetime.minute - (end.hour*60 + end.minute)
            
    def check_values(self, cr, uid, data, context=None):
        data_keys = ['start_time_string', 'end_time_string', 'location_id']
        keys = data.keys()
        if not all([k in data_keys for k in keys]):
            raise osv.except_osv('Error!', 'Not enough data to generate shift')
        if len(data['start_time_string']) < 4:
            raise osv.except_osv('Error!', 'Start time must have 24 hour format HH:MM')
        if len(data['end_time_string']) < 4:
            raise osv.except_osv('Error!', 'End time must have 24 hour format HH:MM')
        if len(data['start_time_string']) < 5:
            data['start_time_string'] = '0'+data['start_time_string']
        if len(data['end_time_string']) < 5:
            data['end_time_string'] = '0'+data['end_time_string']
        startH = int(data['start_time_string'][0:2])
        startM = int(data['start_time_string'][3:5])
        endH = int(data['end_time_string'][0:2])
        endM = int(data['end_time_string'][3:5])
        if startH < 0 or startH > 23:
            raise osv.except_osv('Error!', 'Start hour must be between 0 and 11')
        if endH < 0 or endH > 23:
            raise osv.except_osv('Error!', 'End hour must be between 0 and 11')
        if startM < 0 or startM > 59:
            raise osv.except_osv('Error!', 'Start minutes must be between 0 and 59')
        if endM < 0 or endM > 59:
            raise osv.except_osv('Error!', 'End minutes must be between 0 and 59')
        
        if endH > startH:
            duration = endH*60 + endM - (startH*60 + startM)
        else:
            duration = 24*60 - (startH*60 + startM) + endH*60 + endM
        year = str(2000)
        month = str(dt.min.month)
        day = str(dt.min.day)
        strdate = "{0}-{1}-{2} {3}:{4}:00".format(year, month, day, startH, startM)
        start_date = dt.strptime(strdate, dtf)
        end_date = start_date + td(minutes=duration)
        location = self.pool['nh.clinical.location'].browse(cr, uid, data['location_id'], context=context)
        for sp in location.shift_pattern_ids:
            if (start_date >= dt.strptime(sp.start_time, dtf) and start_date < dt.strptime(sp.end_time, dtf)) or (end_date > dt.strptime(sp.start_time, dtf) and end_date <= dt.strptime(sp.end_time, dtf)):
                raise osv.except_osv('Error!', 'Cannot add overlapping shifts')
            if start_date <= dt.strptime(sp.start_time, dtf) and end_date >= dt.strptime(sp.end_time, dtf):
                raise osv.except_osv('Error!', 'Cannot add overlapping shifts')
        return {
            'start_time': start_date,
            'start_time_string': data['start_time_string'],
            'end_time': end_date, 
            'end_time_string': data['end_time_string'],
            'duration': duration, 
            'location_id': data['location_id']
        }
    
    def create(self, cr, uid, vals, context=None):
        shift_pool = self.pool['nh.clinical.shift']
        data = self.check_values(cr, uid, vals, context=context)
        res = super(nh_clinical_shift_pattern, self).create(cr, uid, data, context=context)
        shift_pool.generate_shifts(cr, uid, data['location_id'], context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        if 'start_time_string' in vals or 'end_time_string' in vals:
            super(nh_clinical_shift_pattern, self).write(cr, uid, ids, {'active': False}, context=context)
        else:
            return True
        shift_pool = self.pool['nh.clinical.shift']
        location_ids = []
        for pattern in self.browse(cr, uid, ids, context=context):
            location_ids.append(pattern.location_id.id)
            next_shift = shift_pool.next_shift(cr, uid, pattern.location_id.id, context=context)
            if next_shift:
                shift_pool.unlink(cr, uid, next_shift, context=context)
            data = {
                'start_time_string': vals.get('start_time_string') if vals.get('start_time_string') else pattern.start_time_string,
                'end_time_string': vals.get('end_time_string') if vals.get('end_time_string') else pattern.end_time_string,
                'location_id': pattern.location_id.id
            }
            create_data = self.check_values(cr, uid, data, context=context)
            super(nh_clinical_shift_pattern, self).create(cr, uid, create_data, context=context)
        [shift_pool.generate_shifts(cr, uid, loc_id, context=context) for loc_id in location_ids]
        return True

    def unlink(self, cr, uid, ids, context=None):
        return super(nh_clinical_shift_pattern, self).write(cr, uid, ids, {'active': False}, context=context)


class nh_clinical_shift(orm.Model):
    _name = 'nh.clinical.shift'

    _columns = {
        'start': fields.datetime('Start Date Time', required=True),
        'end': fields.datetime('End Date Time', required=True),
        'pattern_id': fields.many2one('nh.clinical.shift.pattern', 'Shift Pattern', required=True),
        'location_id': fields.related('pattern_id', 'location_id', type='many2one', obj='nh.clinical.location', string='Location')
    }

    def create(self, cr, uid, vals, context=None):
        # should check there is no overlapping
        res = super(nh_clinical_shift, self).create(cr, uid, vals, context=context)
        activity_pool = self.pool['nh.activity']
        pattern_pool = self.pool['nh.clinical.shift.pattern']
        spell_timespan_pool = self.pool['nh.clinical.spell.timespan']
        pattern = pattern_pool.browse(cr, uid, vals['pattern_id'], context=context)
        spell_ids = activity_pool.search(cr, uid, [
            ['data_model', '=', 'nh.clinical.spell'],
            ['state', 'not in', ['completed', 'cancelled']],
            ['location_id', 'child_of', pattern.location_id.id]], context=context)
        for s_id in spell_ids:
            spell_activity = activity_pool.browse(cr, uid, s_id, context=context)
            spell_timespan_pool.create(cr, uid, {
                'start': vals['start'] if vals['start'] > spell_activity.date_started else spell_activity.date_started,
                'end': vals['end'],
                'shift_id': res,
                'spell_activity_id': s_id}, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        return True

    def current_shift(self, cr, uid, location_id, context=None):
        shift_ids = self.search(cr, uid, [
            ['location_id', '=', location_id],
            ['start', '<=', dt.now().strftime(dtf)],
            ['end', '>', dt.now().strftime(dtf)]
        ], context=context)
        if not shift_ids:
            return False
        else:
            return shift_ids[0]

    def next_shift(self, cr, uid, location_id, context=None):
        shift_ids = self.search(cr, uid, [
            ['location_id', '=', location_id],
            ['start', '>', dt.now().strftime(dtf)]
        ], order='start asc', context=context)
        if not shift_ids:
            return False
        else:
            return shift_ids[0]

    def last_shift(self, cr, uid, location_id, context=None):
        shift_ids = self.search(cr, uid, [
            ['location_id', '=', location_id],
            ['end', '<=', dt.now().strftime(dtf)]
        ], order='start desc', context=context)
        if not shift_ids:
            return False
        else:
            return shift_ids[0]

    def previous_shift(self, cr, uid, location_id, context=None):
        shift_ids = self.search(cr, uid, [
            ['location_id', '=', location_id],
            ['end', '<=', dt.now().strftime(dtf)]
        ], order='start desc', context=context)
        if len(shift_ids) < 2:
            return False
        else:
            return shift_ids[1]

    def generate_shifts(self, cr, uid, location_id, context=None):
        res = {}
        shift_pattern_pool = self.pool['nh.clinical.shift.pattern']
        location = self.pool['nh.clinical.location'].browse(cr, uid, location_id, context=context)
        if not location.shift_pattern_ids:
            return False
        if not self.current_shift(cr, uid, location_id, context=context):
            diff = 1440
            pattern = False
            for shift_pattern in location.shift_pattern_ids:
                if not pattern:
                    pattern = shift_pattern
                    diff = shift_pattern_pool.distance(cr, uid, shift_pattern.id, dt.now(), context=context)
                    continue
                distance = shift_pattern_pool.distance(cr, uid, shift_pattern.id, dt.now(), context=context)
                if distance < diff:
                    diff = distance
                    pattern = shift_pattern
            now = dt.now()
            pattern_start = dt.strptime(pattern.start_time, dtf)
            pattern_end = dt.strptime(pattern.end_time, dtf)
            date_start = dt(year=now.year, month=now.month, day=now.day, hour=pattern_start.hour, minute=pattern_start.minute)
            date_end = dt(year=now.year, month=now.month, day=now.day, hour=pattern_end.hour, minute=pattern_end.minute)
            if date_end < date_start:
                date_end = date_end + td(days=1)
            res['current'] = self.create(cr, uid, {
                'start': date_start.strftime(dtf),
                'end': date_end.strftime(dtf),
                'pattern_id': pattern.id
            }, context=context)
        next_shift = self.next_shift(cr, uid, location_id, context=context)
        if next_shift:
            next_shift_pattern_id = self.browse(cr, uid, next_shift, context=context).pattern_id.id
        else:
            next_shift_pattern_id = False
        diff = 0
        pattern = False
        for shift_pattern in location.shift_pattern_ids:
            if not pattern:
                pattern = shift_pattern
                diff = shift_pattern_pool.distance(cr, uid, shift_pattern.id, dt.now(), context=context)
                continue
            distance = shift_pattern_pool.distance(cr, uid, shift_pattern.id, dt.now(), context=context)
            if distance > diff:
                diff = distance
                pattern = shift_pattern
        if next_shift and next_shift_pattern_id != pattern.id:
            self.unlink(cr, uid, next_shift, context=context)
        elif next_shift and next_shift_pattern_id == pattern.id:
            return res
        now = dt.now()
        pattern_start = dt.strptime(pattern.start_time, dtf)
        pattern_end = dt.strptime(pattern.end_time, dtf)
        date_start = dt(year=now.year, month=now.month, day=now.day, hour=pattern_start.hour, minute=pattern_start.minute)
        date_end = dt(year=now.year, month=now.month, day=now.day, hour=pattern_end.hour, minute=pattern_end.minute)
        if now > date_start:
            date_start = date_start + td(days=1)
            date_end = date_end + td(days=1)
        if date_end < date_start:
            date_end = date_end + td(days=1)
        res['next'] = self.create(cr, uid, {
            'start': date_start.strftime(dtf),
            'end': date_end.strftime(dtf),
            'pattern_id': pattern.id
        }, context=context)
        return res


class nh_clinical_location(orm.Model):
    _inherit = 'nh.clinical.location'

    _columns = {
        'shift_pattern_ids': fields.one2many('nh.clinical.shift.pattern', 'location_id', 'Daily Shifts'),
        'shift_ids': fields.one2many('nh.clinical.shift', 'location_id', 'Historic Shift Log')
    }


class nh_clinical_spell_timespan(orm.Model):
    _name = 'nh.clinical.spell.timespan'

    _columns = {
        'start': fields.datetime('Start Date Time'),
        'end': fields.datetime('End Date Time'),
        'shift_id': fields.many2one('nh.clinical.shift', 'Shift', required=True, ondelete='cascade'),
        'spell_activity_id': fields.many2one('nh.activity', domain=[['data_model', '=', 'nh.clinical.spell']], string='Spell')
    }
    
    _sql_constraints = [
        ('shift_spell_uniq', 'unique(shift_id, spell_activity_id)', 'Spell can only have one timespan per shift!'),
    ]

    def start_timespan(self, cr, uid, spell_activity_id, shift_id, start, context=None):
        shift = self.pool['nh.clinical.shift'].browse(cr, uid, shift_id, context=context)
        return self.create(cr, uid, {
            'start': start if shift.end > start > shift.start else shift.start,
            'end': shift.end,
            'shift_id': shift_id,
            'spell_activity_id': spell_activity_id
        }, context=context)

    def start_patient_timespan(self, cr, uid, patient_identifier, start=False, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        spell_pool = self.pool['nh.clinical.spell']
        location_pool = self.pool['nh.clinical.location']
        shift_pool = self.pool['nh.clinical.shift']
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', patient_identifier]], context=context)
        if not patient_id:
            raise osv.except_osv('Error!', 'Patient not found!')
        spell_id = spell_pool.search(cr, uid, [['patient_id', '=', patient_id[0]], ['activity_id.state', 'not in', ['cancelled', 'completed']]], context=context)
        if not spell_id:
            raise osv.except_osv('Error!', 'Spell not found!')
        spell = spell_pool.browse(cr, uid, spell_id[0], context=context)
        ward_id = location_pool.find_nearest_location_id(cr, uid, spell.activity_id.location_id.id, context=context)
        shift_id = shift_pool.current_shift(cr, uid, ward_id, context=context)
        return self.start_timespan(cr, uid, spell.activity_id.id, shift_id, spell.activity_id.date_started if not start else start, context=context)

    def delete_patient_timespans(self, cr, uid, patient_identifier, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        spell_pool = self.pool['nh.clinical.spell']
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', patient_identifier]], context=context)
        if not patient_id:
            raise osv.except_osv('Error!', 'Patient not found!')
        spell_id = spell_pool.search(cr, uid, [['patient_id', '=', patient_id[0]], ['activity_id.state', 'not in', ['cancelled', 'completed']]], context=context)
        if not spell_id:
            raise osv.except_osv('Error!', 'Spell not found!')
        spell = spell_pool.browse(cr, uid, spell_id[0], context=context)
        timespan_ids = self.search(cr, uid, [['spell_activity_id', '=', spell.activity_id.id]], context=context)
        return self.unlink(cr, uid, timespan_ids, context=context)

    def end_timespan(self, cr, uid, spell_activity_id, context=None):
        timespan_ids = self.search(cr, uid, [
            ['spell_activity_id', '=', spell_activity_id],
            ['start', '<=', dt.now().strftime(dtf)],
            ['end', '>', dt.now().strftime(dtf)]
        ], context=context)
        if not timespan_ids:
            return False
        else:
            return self.write(cr, uid, timespan_ids, {'end': dt.now().strftime(dtf)}, context=context)

    def end_patient_timespan(self, cr, uid, patient_identifier, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        spell_pool = self.pool['nh.clinical.spell']
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', patient_identifier]], context=context)
        if not patient_id:
            raise osv.except_osv('Error!', 'Patient not found!')
        spell_id = spell_pool.search(cr, uid, [['patient_id', '=', patient_id[0]], ['activity_id.state', 'not in', ['cancelled', 'completed']]], context=context)
        if not spell_id:
            raise osv.except_osv('Error!', 'Spell not found!')
        spell = spell_pool.browse(cr, uid, spell_id[0], context=context)
        return self.end_timespan(cr, uid, spell.activity_id.id, context=context)

    def cancel_changes_patient_timespan(self, cr, uid, patient_identifier, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        spell_pool = self.pool['nh.clinical.spell']
        shift_pool = self.pool['nh.clinical.shift']
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', patient_identifier]], context=context)
        if not patient_id:
            raise osv.except_osv('Error!', 'Patient not found!')
        spell_id = spell_pool.search(cr, uid, [['patient_id', '=', patient_id[0]], ['activity_id.state', 'not in', ['cancelled', 'completed']]], context=context)
        if not spell_id:
            raise osv.except_osv('Error!', 'Spell not found!')
        spell = spell_pool.browse(cr, uid, spell_id[0], context=context)
        timespan_ids = self.search(cr, uid, [['spell_activity_id', '=', spell.activity_id.id]], order='end desc', context=context)
        if not timespan_ids:
            return True
        last_timespan = self.browse(cr, uid, timespan_ids[0], context=context)
        if last_timespan.shift_id.location_id.id != spell.activity_id.location_id.id:
            self.unlink(cr, uid, last_timespan.id, context=context)
            return self.cancel_changes_patient_timespan(cr, uid, patient_identifier, context=context)
        self.write(cr, uid, last_timespan.id, {
            'start': last_timespan.shift_id.start if last_timespan.shift_id.start > spell.activity_id.date_started else spell.activity_id.date_started,
            'end': last_timespan.shift_id.end}, context=context)
        current_shift_id = shift_pool.current_shift(cr, uid, last_timespan.shift_id.location_id.id, context=context)
        if last_timespan.shift_id.id != current_shift_id:
            current_shift = shift_pool.browse(cr, uid, current_shift_id, context=context)
            self.create(cr, uid, {
                'start': current_shift.start,
                'end': current_shift.end,
                'shift_id': current_shift.id,
                'spell_activity_id': spell.activity_id.id
            }, context=context)
        else:
            return True
        last_shift_id = shift_pool.last_shift(cr, uid, last_timespan.shift_id.location_id.id, context=context)
        if last_timespan.shift_id.id != last_shift_id:
            last_shift = shift_pool.browse(cr, uid, last_shift_id, context=context)
            self.create(cr, uid, {
                'start': last_shift.start,
                'end': last_shift.end,
                'shift_id': last_shift.id,
                'spell_activity_id': spell.activity_id.id
            }, context=context)
        else:
            return True
        previous_shift_id = shift_pool.previous_shift(cr, uid, last_timespan.shift_id.location_id.id, context=context)
        if last_timespan.shift_id.id != previous_shift_id:
            previous_shift = shift_pool.browse(cr, uid, previous_shift_id, context=context)
            self.create(cr, uid, {
                'start': previous_shift.start,
                'end': previous_shift.end,
                'shift_id': previous_shift.id,
                'spell_activity_id': spell.activity_id.id
            }, context=context)
        else:
            return True
        return True
