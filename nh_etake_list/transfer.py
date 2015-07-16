from openerp.osv import orm, fields
import logging

_logger = logging.getLogger(__name__)


class nh_etake_list_transfer(orm.Model):
    _name = "nh.etake_list.transfer"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Transfer View"
    _rec_name = 'patient_id'
    _auto = False
    _table = "nh_etake_list_transfer"
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
                    where activity.data_model = 'nh.clinical.patient.move' and activity.state not in ('completed','cancelled')
                )
        """ % (self._table, self._table))

    def request(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        for move in self.browse(cr, uid, ids, context=context):
            activity_pool.start(cr, uid, move.id, context=context)
        return True

    def complete(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        for move in self.browse(cr, uid, ids, context=context):
            activity_pool.complete(cr, uid, move.id, context=context)
        return True