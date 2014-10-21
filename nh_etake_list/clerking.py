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

    _state_selection = [['To be Clerked', 'To be Clerked'],
                        ['Clerking', 'Clerking'],
                        ['To be Discharged', 'To be Discharged'],
                        ['Other', 'Other']]

    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'location_id': fields.many2one('nh.clinical.location', 'Ward'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'hospital_number': fields.text('Hospital Number'),
        'nhs_number': fields.text('NHS Number'),
        'state': fields.selection(_state_selection, 'State'),
        'date_started': fields.datetime('Started'),
        'date_terminated': fields.datetime('Completed'),
        'user_id': fields.many2one('res.users', 'Asignee'),
        'doctor_task_ids': fields.one2many('nh.activity', 'parent_id', string='Doctor Tasks', domain="[['data_model','=','nh.clinical.doctor.task']]"),
        'diagnosis': fields.text('Diagnosis'),
        'plan': fields.text('Plan')
    }

    def _get_clerking_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        res = [['To be Clerked', 'To be Clerked'], ['Clerking', 'Clerking'], ['To be Discharged', 'To be Discharged']]
        fold = {r[0]: False for r in res}
        return res, fold

    _group_by_full = {
        'state': _get_clerking_groups,
    }

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        if 'doctor_task_ids' in fields:
            activity_pool = self.pool['nh.activity']
            fields.remove('doctor_task_ids')
            read_values = super(nh_etake_list_clerking, self).read(cr, uid, ids, fields, context, load)
            for rv in read_values:
                rv['doctor_task_ids'] = activity_pool.search(cr, uid, [['parent_id', '=', rv['id']], ['data_model', '=', 'nh.clinical.doctor.task']], context=context)
            return read_values
        return super(nh_etake_list_clerking, self).read(cr, uid, ids, fields, context, load)

    def write(self, cr, uid, ids, vals, context=None):
        activity_pool = self.pool['nh.activity']
        for clerking in self.browse(cr, uid, ids, context=context):
            if 'diagnosis' in vals:
                if clerking.state not in ['To be Clerked', 'Clerking']:
                    raise osv.except_osv('Error!', 'The patient has already been clerked!')
                activity_pool.submit(cr, uid, clerking.activity_id.id, {'diagnosis': vals['diagnosis']}, context=context)
                activity_pool.submit(cr, uid, clerking.id, {'diagnosis': vals['diagnosis']}, context=context)
            if 'plan' in vals:
                if clerking.state not in ['To be Clerked', 'Clerking']:
                    raise osv.except_osv('Error!', 'The patient has already been clerked!')
                activity_pool.submit(cr, uid, clerking.activity_id.id, {'plan': vals['plan']}, context=context)
                activity_pool.submit(cr, uid, clerking.id, {'doctor_plan': vals['plan']}, context=context)
            if 'doctor_task_ids' in vals:
                for dt in vals['doctor_task_ids']:
                    activity_pool.write(cr, uid, dt[1], dt[2], context=context)
        return True

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        spell_activity.id as id,
                        clerking_activity.id as activity_id,
                        case
                            when discharge_activity.state is not null and discharge_activity.state = 'completed' then 'Discharged'
                            when discharge_activity.state is not null and discharge_activity.state != 'completed' then 'To be Discharged'
                            when clerking_activity.state = 'scheduled' then 'To be Clerked'
                            when clerking_activity.state = 'started' then 'Clerking'
                            else 'Other'
                        end as state,
                        clerking_activity.date_started as date_started,
                        clerking_activity.date_terminated as date_terminated,
                        clerking_activity.user_id as user_id,
                        spell.patient_id as patient_id,
                        spell.diagnosis as diagnosis,
                        spell.doctor_plan as plan,
                        location.id as location_id,
                        patient.other_identifier as hospital_number,
                        patient.patient_identifier as nhs_number
                    from nh_clinical_spell spell
                    inner join nh_activity spell_activity on spell_activity.id = spell.activity_id
                    inner join nh_clinical_patient patient on spell.patient_id = patient.id
                    inner join nh_activity clerking_activity on clerking_activity.parent_id = spell_activity.id and clerking_activity.data_model = 'nh.clinical.patient.clerking'
                    left join nh_activity discharge_activity on discharge_activity.parent_id = spell_activity.id and discharge_activity.data_model = 'nh.clinical.adt.patient.discharge'
                    left join nh_clinical_location location on location.id = spell.location_id
                )
        """ % (self._table, self._table))

    def start(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        for clerking in self.browse(cr, uid, ids, context=context):
            if clerking.state != 'scheduled':
                raise osv.except_osv('Error!', 'This clerking has already started!')
            activity_pool.start(cr, uid, clerking.activity_id.id, context=context)
            activity_pool.write(cr, uid, clerking.activity_id.id, {'user_id': uid}, context=context)
        return True

    def create_task(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context=context)

        context.update({'default_patient_id': data.patient_id.id, 'default_spell_id': data.id})
        return {
            'name': 'Add Task',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.doctor_task_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context
        }

    def complete(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        for clerking in self.browse(cr, uid, ids, context=context):
            if clerking.state != 'started':
                raise osv.except_osv('Error!', 'This clerking has already been completed!')
            if clerking.user_id.id != uid:
                raise osv.except_osv('Error!', 'You cannot complete this clerking, someone else started it!')
            activity_pool.complete(cr, uid, clerking.activity_id.id, context=context)
        return True