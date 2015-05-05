from openerp.osv import orm, fields, osv
import logging
from openerp import SUPERUSER_ID
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf
from lxml import etree

_logger = logging.getLogger(__name__)

class nh_clinical_doctor_task(orm.Model):
    _name = 'nh.clinical.doctor.task'
    _inherit = 'nh.clinical.doctor.task'

    _columns = {
        'summary': fields.related('activity_id', 'summary', string='Summary', type='char'),
        'state': fields.related('activity_id', 'state', string='State', type='char'),
        'date_terminated': fields.related('activity_id', 'date_terminated', string='Date Terminated', type='datetime')
    }

    def ov_complete(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        for doctor_task in self.browse(cr, uid, ids, context=context):
            activity_pool.complete(cr, uid, doctor_task.activity_id.id, context=context)
        return True


class nh_etake_list_overview(orm.Model):
    _name = "nh.etake_list.overview"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "eTake List Patient Overview"
    _rec_name = 'patient_id'
    _auto = False
    _table = "nh_etake_list_overview"

    _state_selection = [['To be Clerked', 'To be Clerked'],
                        ['Senior Review', 'Senior Review'],
                        ['Consultant Review', 'Consultant Review'],
                        ['Discharged', 'Discharged'],
                        ['To be Discharged', 'To be Discharged'],
                        ['Other', 'Other'],
                        ['Referral', 'Referral'],
                        ['TCI', 'To Come In'],
                        ['Clerking in Process', 'Clerking in Progress'],
                        ['Done', 'Done'],
                        ['to_dna', 'DNA'],
                        ['dna', 'DNA'],
                        ['admitted', 'Admitted']]
    _stage_selection = [['referral', 'Referral'], ['tci', 'To Come In'], ['tbc', 'To be Clerked'],
                        ['cip', 'Clerking in Progress'], ['sr', 'Senior Review'], ['cr', 'Consultant Review'],
                        ['tbd', 'To Be Discharged'], ['d', 'Discharged']]
    _gender = [['M', 'Male'], ['F', 'Female']]

    def _get_dt_ids(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        doctor_task_pool = self.pool['nh.clinical.doctor.task']
        for ov in self.browse(cr, uid, ids, context=context):
            res[ov.id] = doctor_task_pool.search(cr, uid, [['activity_id.parent_id', '=', ov.spell_activity_id.id]])
        return res

    def _get_ward_id(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        location_pool = self.pool['nh.clinical.location']
        for ov in self.browse(cr, uid, ids, context=context):
            res[ov.id] = ov.location_id.id if ov.location_id.usage == 'ward' \
                else location_pool.get_closest_parent_id(cr, uid, ov.location_id.id, 'ward', context=context)
        return res

    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'spell_activity_id': fields.many2one('nh.activity', 'Spell Activity'),
        'location_id': fields.many2one('nh.clinical.location', 'Location'),
        'location_type': fields.char('Location Type', size=10),
        'ward_id': fields.function(_get_ward_id, type='many2one', relation='nh.clinical.location', string='Ward'),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'hospital_number': fields.text('Hospital Number'),
        'nhs_number': fields.text('NHS Number'),
        'state': fields.selection(_state_selection, 'State'),
        'stage': fields.selection(_stage_selection, 'Stage'),
        'gender': fields.selection(_gender, 'Gender'),
        'age': fields.integer('Age'),
        'dob': fields.datetime('Date of Birth'),
        'form_id': fields.many2one('nh.clinical.patient.referral.form', 'Referral Form'),
        'clerking_started': fields.datetime('Clerking Started'),
        'clerking_terminated': fields.datetime('Clerking Finished'),
        'review_terminated': fields.datetime('Reviewed'),
        'discharge_terminated': fields.datetime('Discharged'),
        'ptwr_terminated': fields.datetime('PTWR Done'),
        'hours_from_discharge': fields.integer('Hours since Discharge'),
        'hours_from_ptwr': fields.integer('Hours since PTWR'),
        'review_deadline_polarity': fields.char('Review Deadline Polarity', size=1),
        'review_deadline': fields.char('Review Deadline', size=15),
        'diagnosis': fields.text('Diagnosis'),
        'plan': fields.text('Plan'),
        'clerking_user_id': fields.many2one('res.users', 'Clerking by'),
        'review_user_id': fields.many2one('res.users', 'Senior Review by'),
        'discharge_user_id': fields.many2one('res.users', 'Discharged by'),
        'ptwr_user_id': fields.many2one('res.users', 'Consultant Review by'),
        'doctor_task_ids': fields.function(_get_dt_ids, type='many2many', relation='nh.clinical.doctor.task', string='Doctor Tasks'),
        'dna_able': fields.boolean('Can be marked as DNA'),
        'doctor_tasks': fields.integer('Doctor Tasks'),
        'blocking_tasks': fields.integer('Blocking Tasks'),
        'specialty_id': fields.many2one('nh.clinical.specialty', 'Specialty')
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    with dt as (
                        select
                            activity.id as id,
                            activity.state as state,
                            activity.parent_id as parent_id,
                            data.blocking as blocking
                        from nh_activity activity
                        inner join nh_clinical_doctor_task data on data.activity_id = activity.id and activity.data_model = 'nh.clinical.doctor.task'
                        where state != 'completed' and state != 'cancelled'
                    )
                    select
                        patient.id as id,
                        patient.gender as gender,
                        patient.dob as dob,
                        extract(year from age(now(), patient.dob)) as age,
                        tci_activity.pos_id as pos_id,
                        (select count(*) from dt where dt.parent_id = spell_activity.id) as doctor_tasks,
                        (select count(*) from dt where dt.parent_id = spell_activity.id and dt.blocking) as blocking_tasks,
                        case
                            when referral_activity.state is null and tci_activity.state is null then 'Done'
                            when spell_activity.state = 'cancelled' then 'Done'
                            when ptwr_activity.state is not null and ptwr_activity.state = 'completed' then 'admitted'
                            when discharge_activity.state is not null and discharge_activity.state = 'completed' then 'Discharged'
                            when discharge_activity.state is not null and discharge_activity.state != 'completed' then 'To be Discharged'
                            when referral_activity.state is not null and referral_activity.state != 'completed' and referral_activity.state != 'cancelled' then 'Referral'
                            when tci_activity.state is not null and tci_activity.state = 'cancelled' then 'dna'
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' and (extract(epoch from now() at time zone 'UTC' - tci_activity.date_scheduled) / 3600) >= 96 then 'to_dna'
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' then 'TCI'
                            when clerking_activity.state = 'scheduled' then 'To be Clerked'
                            when clerking_activity.state = 'started' then 'Clerking in Process'
                            when ptwr_activity.state is not null and ptwr_activity.state != 'completed' and ptwr_activity.state != 'cancelled' then 'Consultant Review'
                            when review_activity.state = 'scheduled' then 'Senior Review'
                            else 'Other'
                        end as state,
                        case
                            when referral_activity.state is null and tci_activity.state is null then null
                            when spell_activity.state = 'cancelled' then null
                            when discharge_activity.state is not null and discharge_activity.state = 'completed' then 'discharged'
                            when discharge_activity.state is not null and discharge_activity.state != 'completed' then 'tbd'
                            when referral_activity.state is not null and referral_activity.state != 'completed' and referral_activity.state != 'cancelled' then 'referral'
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' then 'tci'
                            when clerking_activity.state = 'scheduled' then 'tbc'
                            when clerking_activity.state = 'started' then 'cip'
                            when ptwr_activity.state is not null and ptwr_activity.state != 'completed' and ptwr_activity.state != 'cancelled' then 'cr'
                            when review_activity.state = 'scheduled' then 'sr'
                            else null
                        end as stage,
                        case
                            when tci_activity.state is null then FALSE
                            when tci_activity.state is not null and tci_activity.state != 'scheduled' then FALSE
                            when now() at time zone 'UTC' >= ((extract(YEAR FROM tci_activity.date_scheduled) || '-' ||  extract(MONTH FROM tci_activity.date_scheduled) || '-' || extract(DAY FROM tci_activity.date_scheduled) || ' 08:00:00')::timestamp + '1 day') then TRUE
                            else FALSE
                        end as dna_able,
                        patient.id as patient_id,
                        case
                            when tci_activity.state = 'scheduled' then tci_activity.location_id
                            else location.id
                        end as location_id,
                        case
                            when tci_activity.state = 'scheduled' then 'ward'
                            else location.usage
                        end as location_type,
                        case
                            when referral_activity.state is not null and referral_activity.state != 'completed' and referral_activity.state != 'cancelled' then referral_activity.id
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' then tci_activity.id
                            when clerking_activity.state = 'scheduled' or clerking_activity.state = 'started' then clerking_activity.id
                            when review_activity.state = 'scheduled' then review_activity.id
                            when ptwr_activity.state = 'new' or ptwr_activity.state = 'scheduled' or ptwr_activity.state = 'completed' then ptwr_activity.id
                            when discharge_activity.state = 'new' or discharge_activity.state = 'scheduled' or discharge_activity.state = 'completed' then discharge_activity.id
                            else spell_activity.id
                        end as activity_id,
                        spell_activity.id as spell_activity_id,
                        patient.other_identifier as hospital_number,
                        case
                            when char_length(patient.patient_identifier) > 6 then substring(patient.patient_identifier from 1 for 3) || '-' || substring(patient.patient_identifier from 4 for 3) || '-' || substring(patient.patient_identifier from 7)
                            else patient.patient_identifier
                        end as nhs_number,
                        referral.form_id as form_id,
                        form.specialty_id as specialty_id,
                        clerking_activity.date_started as clerking_started,
                        clerking_activity.date_terminated as clerking_terminated,
                        clerking_activity.user_id as clerking_user_id,
                        review_activity.date_terminated as review_terminated,
                        review_activity.terminate_uid as review_user_id,
                        ptwr_activity.date_terminated as ptwr_terminated,
                        ptwr_activity.user_id as ptwr_user_id,
                        case
                            when ptwr_activity.date_terminated is null then 0
                            else extract(epoch from now() at time zone 'UTC' - ptwr_activity.date_terminated) / 3600
                        end as hours_from_ptwr,
                        spell.diagnosis as diagnosis,
                        spell.doctor_plan as plan,
                        discharge_activity.date_terminated as discharge_terminated,
                        case
                            when discharge_activity.date_terminated is null then 0
                            else extract(epoch from now() at time zone 'UTC' - discharge_activity.date_terminated) / 3600
                        end as hours_from_discharge,
                        discharge_activity.terminate_uid as discharge_user_id,
                        case
                            when tci_activity.date_terminated is null then ''
                            when (tci_activity.date_terminated + interval '14 hours') >= now() at time zone 'UTC' then ''
                            else '-'
                        end as review_deadline_polarity,
                        case
                            when tci_activity.date_terminated is null then '14H 00M'
                            when @ extract(days from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') > 0 then @ extract(days from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'D ' || extract(hours from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'H ' || @ extract(minutes from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'M'
                            else @ extract(hours from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'H ' || @ extract(minutes from (tci_activity.date_terminated + interval '14 hours') - now() at time zone 'UTC') || 'M'
                        end as review_deadline

                    from nh_clinical_patient patient
                    left join nh_clinical_spell spell on spell.patient_id = patient.id
                    left join nh_activity spell_activity on spell_activity.id = spell.activity_id
                    left join nh_activity referral_activity on referral_activity.patient_id = patient.id and referral_activity.data_model = 'nh.clinical.patient.referral'
                    left join nh_clinical_patient_referral referral on referral.activity_id = referral_activity.id
                    left join nh_clinical_patient_referral_form form on referral.form_id = form.id
                    left join nh_activity tci_activity on tci_activity.parent_id = spell_activity.id and tci_activity.data_model = 'nh.clinical.patient.tci'
                    left join nh_activity discharge_activity on discharge_activity.parent_id = spell_activity.id and discharge_activity.data_model = 'nh.clinical.adt.patient.discharge'
                    left join nh_activity clerking_activity on clerking_activity.parent_id = spell_activity.id and clerking_activity.data_model = 'nh.clinical.patient.clerking'
                    left join nh_activity review_activity on review_activity.parent_id = spell_activity.id and review_activity.data_model = 'nh.clinical.patient.review'
                    left join nh_activity ptwr_activity on ptwr_activity.parent_id = spell_activity.id and ptwr_activity.data_model = 'nh.clinical.ptwr'
                    left join nh_clinical_location location on location.id = spell_activity.location_id
                    where referral_activity.id is not null or tci_activity.id is not null
                )
        """ % (self._table, self._table))

    def _get_overview_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        res = [
            ['Referral', 'Referral'],
            ['TCI', 'To Come In'],
            ['To be Clerked', 'To be Clerked'],
            ['Clerking in Process', 'Clerking in Progress'],
            ['Senior Review', 'Senior Review'],
            ['Consultant Review', 'Consultant Review'],
            ['To be Discharged', 'To be Discharged'],
            ['Discharged', 'Discharged']
        ]
        fold = {r[0]: False for r in res}
        return res, fold

    _group_by_full = {
        'state': _get_overview_groups,
    }

    def write(self, cr, uid, ids, vals, context=None):
        activity_pool = self.pool['nh.activity']
        for ov in self.browse(cr, uid, ids, context=context):
            if 'diagnosis' in vals:
                if ov.state not in ['To be Clerked', 'Clerking in Process']:
                    raise osv.except_osv('Error!', 'The patient has already been clerked!')
                activity_pool.submit(cr, uid, ov.activity_id.id, {'diagnosis': vals['diagnosis']}, context=context)
                activity_pool.submit(cr, uid, ov.spell_activity_id.id, {'diagnosis': vals['diagnosis']}, context=context)
            if 'plan' in vals:
                if ov.state not in ['To be Clerked', 'Clerking in Process']:
                    raise osv.except_osv('Error!', 'The patient has already been clerked!')
                activity_pool.submit(cr, uid, ov.activity_id.id, {'plan': vals['plan']}, context=context)
                activity_pool.submit(cr, uid, ov.spell_activity_id.id, {'doctor_plan': vals['plan']}, context=context)
        return True

    def complete_referral(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'Referral':
            raise osv.except_osv('Error!', 'Trying to complete referral out of Referral state')
        user_pool = self.pool['res.users']
        user = user_pool.browse(cr, uid, uid, context=context)
        location_ids = [l.id for l in user.location_ids if any([c.name == 'etakelist' for c in l.context_ids])]
        tci_location_id = location_ids[0] if location_ids else False
        context.update({'default_referral_activity_id': ov['activity_id'][0], 'default_tci_location_id': tci_location_id})
        return {
            'name': 'Accept Referral',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.etake_list.accept_referral_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context
        }

    def complete_tci(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'TCI':
            raise osv.except_osv('Error!', 'The patient is not in To Come In state')
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, ov['activity_id'][0], context=context)
        return True

    def complete_clerking(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'Clerking in Process':
            raise osv.except_osv('Error!', 'Trying to complete clerking out of Clerking in Process state')
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, ov['activity_id'][0], context=context)
        return True

    def complete_ptwr(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'Consultant Review':
            raise osv.except_osv('Error!', 'Trying to complete Consultant Review out of Consultant Review state')
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, ov['activity_id'][0], context=context)
        return True

    def cancel_referral(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'Referral':
            raise osv.except_osv('Error!', 'Trying to cancel referral out of Referral state')
        activity_pool.cancel(cr, uid, ov['activity_id'][0], context=context)
        return True

    def complete_current_stage(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['activity_id'], context=context)
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, ov['activity_id'][0], context=context)
        return True

    def cancel_tci(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'patient_id', 'activity_id'], context=context)
        if ov['state'] != 'TCI':
            raise osv.except_osv('Error!', 'Trying to cancel patient arrival out of To Come In state')
        activity_pool = self.pool['nh.activity']
        activity_pool.cancel(cr, uid, ov['activity_id'][0], context=context)
        discharge_pool = self.pool['nh.clinical.patient.discharge']
        discharge_activity_id = discharge_pool.create_activity(
            cr, SUPERUSER_ID, {}, {
                'patient_id': ov['patient_id'][0],
                'discharge_date': dt.now().strftime(dtf)}, context=context)
        activity_pool.complete(cr, uid, discharge_activity_id, context=context)
        return True

    def start_clerking(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'To be Clerked':
            raise osv.except_osv('Error!', 'Trying to start patient clerking out of To be Clerked state')
        activity_pool = self.pool['nh.activity']
        activity_pool.start(cr, uid, ov['activity_id'][0], context=context)
        activity_pool.assign(cr, uid, ov['activity_id'][0], uid, context=context)
        return {
            'name': 'Clerking',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.etake_list.overview',
            'res_id': ids[0],
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current_edit',
            'context': context
        }

    def complete_review(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'patient_id', 'spell_activity_id', 'activity_id'], context=context)
        if ov['state'] != 'Senior Review':
            raise osv.except_osv('Error!', 'Trying to complete patient review out of Senior Review state')
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, ov['activity_id'][0], context=context)
        ptwr_pool = self.pool['nh.clinical.ptwr']
        ptwr_pool.create_activity(cr, uid, {
            'patient_id': ov['patient_id'][0],
            'parent_id': ov['spell_activity_id'][0],
            'creator_id': ov['activity_id'][0]
        }, {}, context=context)
        return True

    def to_be_discharged(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'patient_id', 'spell_activity_id', 'activity_id', 'hospital_number'], context=context)
        if ov['state'] != 'Senior Review':
            raise osv.except_osv('Error!', 'Trying to complete patient review out of Senior Review state')
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, ov['activity_id'][0], context=context)
        discharge_pool = self.pool['nh.clinical.adt.patient.discharge']
        discharge_pool.create_activity(cr, uid, {
            'patient_id': ov['patient_id'][0],
            'parent_id': ov['spell_activity_id'][0],
            'creator_id': ov['activity_id'][0]
        }, {'other_identifier': ov['hospital_number']}, context=context)
        return True

    def discharge(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['state', 'doctor_task_ids', 'activity_id'], context=context)
        doctor_task_pool = self.pool['nh.clinical.doctor.task']
        if ov['state'] != 'To be Discharged':
            raise osv.except_osv('Error!', 'Trying to discharge patient out of To be Discharged state')
        if any([dtask['blocking'] for dtask in doctor_task_pool.read(cr, uid, ov['doctor_task_ids'], ['state', 'blocking'], context=context) if dtask['state'] != 'completed']):
            raise osv.except_osv('Error!', 'Patient cannot be discharged before the blocking tasks are completed!')
        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, ov['activity_id'][0], context=context)
        return True

    def create_task(self, cr, uid, ids, context=None):
        ov = self.read(cr, uid, ids[0], ['patient_id', 'spell_activity_id'], context=context)

        context.update({'default_patient_id': ov['patient_id'][0], 'default_spell_id': ov['spell_activity_id'][0]})
        return {
            'name': 'Add Task',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.doctor_task_wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'new',
            'context': context
        }

    def remove_dna_patients(self, cr, uid, context=None):
        dna_patient_ids = self.search(cr, uid, [['state', '=', 'to_dna']], context=context)
        return all([self.cancel_tci(cr, SUPERUSER_ID, [p_id], context=context) for p_id in dna_patient_ids])

    def rollback_action(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        ov = self.browse(cr, uid, ids[0], context=context)
        if not ov.activity_id.creator_id:
            return False
        activity_pool.cancel(cr, uid, ov.activity_id.id, context=context)
        activity_pool.write(cr, uid, ov.activity_id.id, {'parent_id': False}, context=context)
        activity_pool.write(cr, uid, ov.activity_id.creator_id.id, {'state': 'scheduled', 'terminate_uid': False, 'date_terminated': False}, context=context)
        return True

    def rollback_tbc(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'Clerking in Process':
            raise osv.except_osv('Error!', 'Trying to rollback clerking start out of Clerking in Progress state')
        activity_pool.write(cr, uid, ov['activity_id'][0], {'state': 'scheduled', 'user_id': False, 'date_started': False}, context=context)
        return True

    def rollback_ptwr(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id'], context=context)
        if ov['state'] != 'admitted':
            raise osv.except_osv('Error!', 'Trying to rollback consultant review out of Admitted state')
        activity_pool.write(cr, uid, ov['activity_id'][0], {'state': 'scheduled', 'terminate_uid': False, 'date_terminated': False}, context=context)
        return True

    def rollback_discharge(self, cr, uid, ids, context=None):
        activity_pool = self.pool['nh.activity']
        ov = self.browse(cr, uid, ids[0], context=context)
        ov = self.read(cr, uid, ids[0], ['state', 'activity_id', 'patient_id', 'spell_activity_id'], context=context)
        if ov['state'] != 'Discharged':
            raise osv.except_osv('Error!', 'Trying to rollback discharge out of Discharged state')
        spell_ids = activity_pool.search(cr, uid, [['patient_id', '=', ov['patient_id'][0]], ['state', 'not in', ['completed', 'cancelled']]], context=context)
        if spell_ids:
            raise osv.except_osv('Error!', "Can't rollback the discharge. The patient already has an open spell")
        activity_pool.write(cr, uid, ov['activity_id'][0], {'state': 'new', 'terminate_uid': False, 'date_terminated': False}, context=context)
        activity_pool.write(cr, uid, ov['spell_activity_id'][0], {'state': 'started', 'terminate_uid': False, 'date_terminated': False}, context=context)
        return True

    def print_paper_takelist(self, cr, uid, ids, context=None):
        '''This function prints the picking list'''
        context = dict(context or {}, active_ids=ids)
        return self.pool.get("report").get_action(cr, uid, [], 'nh_etake_list.takelist_report_view', context=context)

    def check_etake_list_presence(self, cr, uid, patient_id, context=None):
        states = ['Discharged', 'Other', 'Done', 'dna', 'admitted']
        if not self.search(cr, uid, [['patient_id', '=', patient_id], ['state', 'in', states]], context=context):
            raise osv.except_osv('eTake List Error!', 'The selected patient is already in the eTake List.')
        return True

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        # 349 appears to be form view screen, also test for view_type == 'form'
        # arch is an XML thing so maybe go in and change edit if possible
        # need to find way of getting record ID
        if context is None:
            context = {}
        res = super(nh_etake_list_overview, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        params = context and context.get('params', False) or False
        record_id = False
        if params:
           record_id = params.get('id', False)
        else:
            record_id = context and context.get('active_id', False) or False
        active_model = context.get('active_model')

        if not record_id or (active_model and active_model != 'nh.etake_list.overview') or view_type != 'form':
            return res

        record = self.read(cr, uid, record_id, ['state'], context=context)
        record_state = record.get('state', False)
        # TODO: Shout at Joel for not changing the Clerking in Process issue on both sides of state attr
        if record_state and record_state in ['Senior Review', 'Clerking in Process']:
            doc = etree.XML(res['arch'])
            form_nodes = doc.xpath("//form")
            for form_node in form_nodes:
                form_node.set('edit', '1')
            res['arch'] = etree.tostring(doc)
        return res








class nh_clinical_patient_referral_form(orm.Model):
    _name = 'nh.clinical.patient.referral.form'
    _inherit = 'nh.clinical.patient.referral.form'

    def onchange_patient_id(self, cr, uid, ids, patient_id, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        etl_pool = self.pool['nh.etake_list.overview']
        if not patient_id:
            return {}
        etl_pool.check_etake_list_presence(cr, uid, patient_id, context=context)
        patient = patient_pool.browse(cr, uid, patient_id, context=context)
        return {
            'value': {
                'hospital_number': patient.other_identifier,
                'nhs_number': patient.patient_identifier if patient.patient_identifier else patient.unverified_nhs,
                'first_name': patient.given_name,
                'middle_names': patient.middle_names,
                'last_name': patient.family_name,
                'dob': patient.dob,
                'gender': patient.gender if patient.gender in [g[0] for g in self._gender] else False,
                'ethnicity': patient.ethnicity if patient.ethnicity in [e[0] for e in self._ethnicity] else False,
            }
        }

    def create(self, cr, uid, vals, context=None):
        if vals.get('patient_id'):
            etl_pool = self.pool['nh.etake_list.overview']
            etl_pool.check_etake_list_presence(cr, uid, vals.get('patient_id'), context=context)
        return super(nh_clinical_patient_referral_form, self).create(cr, uid, vals, context=context)


class nh_clinical_patient_tci(orm.Model):
    _name = 'nh.clinical.patient.tci'
    _inherit = 'nh.clinical.patient.tci'

    def create(self, cr, uid, vals, context=None):
        res = super(nh_clinical_patient_tci, self).create(cr, uid, vals, context=context)
        tci_data = self.browse(cr, uid, res, context=context)
        activity_pool = self.pool['nh.activity']
        referral_ids = activity_pool.search(cr, uid, [
            ['patient_id', '=', tci_data.patient_id.id],
            ['state', 'not in', ['completed', 'cancelled']],
            ['data_model', '=', 'nh.clinical.patient.referral']], context=context)
        for rid in referral_ids:
            activity_pool.cancel(cr, uid, rid, context=context)
        return res