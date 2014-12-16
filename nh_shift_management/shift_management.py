# -*- coding: utf-8 -*-
from openerp.osv import orm, osv, fields
from datetime import datetime as dt, timedelta as td
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
import logging
from openerp import SUPERUSER_ID


_logger = logging.getLogger(__name__)


class nh_clinical_daily_shift(orm.Model):
    _name = 'nh.clinical.daily.shift'
    _description = "Location daily shift"

    _columns = {
        'start_time': fields.datetime('Start Time'),
        'start_time_string': fields.char('Start Time', size=5, required=True),
        'end_time': fields.datetime('End Time'),
        'end_time_string': fields.char('End Time', size=5, required=True),
        'duration': fields.integer('Duration (minutes)'),
        'location_id': fields.many2one('nh.clinical.location', 'Location', required=True)
    }

    def generate_shift(self, cr, uid, data, context=None):
        """ Creates a new shift and returns the new ID
        :param data: should contain this structure:
                {
                    'start_time': XX:XX 24 hour format                    
                    'end_time': XX:XX 24 hour format                    
                    'location_id': id of the location
                }
        """
        data_keys = ['start_time_string', 'end_time_string', 'location_id']
        keys = data.keys()
        if not all([k in data_keys for k in keys]):
            raise osv.except_osv('Error!', 'Not enough data to generate shift')
        if len(data['start_time_string']) < 4:
            raise osv.except_osv('Error!', 'Start time must have 24 hour format HH:MM')
        if len(data['end_time_string']) < 4:
            raise osv.except_osv('Error!', 'Start time must have 24 hour format HH:MM')
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
        for ds in location.daily_shift_ids:
            if (start_date >= dt.strptime(ds.start_time, dtf) and start_date < dt.strptime(ds.end_time, dtf)) or (end_date > dt.strptime(ds.start_time, dtf) and end_date <= dt.strptime(ds.end_time, dtf)):
                raise osv.except_osv('Error!', 'Cannot add overlapping shifts')
            if start_date <= dt.strptime(ds.start_time, dtf) and end_date >= dt.strptime(ds.end_time, dtf):
                raise osv.except_osv('Error!', 'Cannot add overlapping shifts')
        return super(nh_clinical_daily_shift, self).create(cr, uid, {
            'start_time': start_date,
            'start_time_string': data['start_time_string'],
            'end_time': end_date, 
            'end_time_string': data['end_time_string'],
            'duration': duration, 
            'location_id': data['location_id']
        }, context=context)
    
    def create(self, cr, user, vals, context=None):        
        return self.generate_shift(cr, user, vals, context=context)


class nh_clinical_location(orm.Model):
    _inherit = 'nh.clinical.location'

    _columns = {
        'daily_shift_ids': fields.one2many('nh.clinical.daily.shift', 'location_id', 'Daily Shifts')
    }