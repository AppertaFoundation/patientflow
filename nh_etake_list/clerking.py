from openerp.osv import orm, fields, osv
import logging

_logger = logging.getLogger(__name__)


class nh_etake_list_clerking(orm.Model):
    _name = "nh.etake_list.clerking"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Clerking View"
    _rec_name = 'patient_id'
    _auto = False
    _table = "nh_etake_list_clerking"
    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'location_id': fields.many2one('nh.clinical.location', 'Ward'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'hospital_number': fields.text('Hospital Number'),
        'state': fields.text('State'),
        'date_started': fields.datetime('Started'),
        'date_terminated': fields.datetime('Completed'),
        'user_id': fields.many2one('res.users', 'Asignee')
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        activity.id as id,
                        activity.id as activity_id,
                        activity.location_id as location_id,
                        activity.patient_id as patient_id,
                        activity.user_id as user_id,
                        activity.state as state,
                        activity.date_started as date_started,
                        activity.date_terminated as date_terminated,
                        patient.other_identifier as hospital_number
                    from nh_activity activity
                    inner join nh_clinical_patient patient on activity.patient_id = patient.id
                    where activity.data_model = 'nh.clinical.patient.clerking' and activity.state not in ('completed','cancelled')
                )
        """ % (self._table, self._table))

    def start(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        for clerking in self.browse(cr, uid, ids, context=context):
            if clerking.state != 'scheduled':
                osv.except_osv('Error!', 'This clerking has already started!')
            activity_pool.start(cr, uid, clerking.id, context=context)
            activity_pool.write(cr, uid, clerking.id, {'user_id': uid}, context=context)
        return True

    def complete(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        for clerking in self.browse(cr, uid, ids, context=context):
            if clerking.state != 'started':
                osv.except_osv('Error!', 'This clerking has already been completed!')
            if clerking.user_id.id != uid:
                osv.except_osv('Error!', 'You cannot complete this clerking, someone else started it!')
            activity_pool.complete(cr, uid, clerking.id, context=context)
        return True