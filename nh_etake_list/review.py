from openerp.osv import orm, fields, osv
from openerp import SUPERUSER_ID
from openerp.addons.nh_activity.activity import except_if
import logging

_logger = logging.getLogger(__name__)


class nh_etake_list_review(orm.Model):
    _name = "nh.etake_list.review"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Review View"
    _rec_name = 'patient_id'
    _auto = False
    _table = "nh_etake_list_review"
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
                    where activity.data_model = 'nh.clinical.patient.review' and activity.state not in ('completed','cancelled')
                )
        """ % (self._table, self._table))

    def transfer(self, cr, uid, ids, context=None):
        move_pool = self.pool['nh.clinical.patient.move']
        api_pool = self.pool['nh.clinical.api']
        activity_pool = self.pool['nh.activity']
        for review in self.browse(cr, uid, ids, context=context):
            spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, review.patient_id.id, context=context)
            except_if(not spell_activity_id, msg="Spell not found!")
            move_id = move_pool.create_activity(cr, uid, {
                'parent_id': spell_activity_id,
                'creator_id': review.id
            }, {'patient_id': review.patient_id.id}, context=context)
            activity_pool.submit(cr, uid, review.id, {'location_id': review.location_id.id}, context=context)
            activity_pool.complete(cr, uid, review.id, context=context)
        return True

    def discharge(self, cr, uid, ids, context=None):
        discharge_pool = self.pool['nh.clinical.adt.patient.discharge']
        api_pool = self.pool['nh.clinical.api']
        activity_pool = self.pool['nh.activity']
        for review in self.browse(cr, uid, ids, context=context):
            spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, review.patient_id.id, context=context)
            except_if(not spell_activity_id, msg="Spell not found!")
            doctor_task_ids = activity_pool.search(cr, uid, [
                ['data_model', '=', 'nh.clinical.doctor.task'],
                ['parent_id', '=', spell_activity_id],
                ['state', 'not in', ['completed', 'cancelled']]
            ], context=context)
            if doctor_task_ids:
                osv.except_osv('Error!', 'Cannot discharge a patient until all his tasks are done!')
            discharge_id = discharge_pool.create_activity(cr, uid, {
                'parent_id': spell_activity_id,
                'creator_id': review.id
            }, {'other_identifier': review.patient_id.other_identifier}, context=context)
            activity_pool.submit(cr, uid, review.id, {'location_id': review.location_id.id}, context=context)
            activity_pool.complete(cr, uid, review.id, context=context)
        return True