from openerp.osv import orm, fields
import logging
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class nh_etake_list_referral(orm.Model):
    _name = "nh.etake_list.referral"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Referral View"
    _rec_name = 'patient_id'
    _auto = False
    _table = "nh_etake_list_referral"

    _state_selection = [['To be Clerked', 'To be Clerked'],
                        ['Referral', 'Referral'],
                        ['Done', 'Done']]
    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'location_id': fields.many2one('nh.clinical.location', 'Ward'),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'hospital_number': fields.text('Hospital Number'),
        'nhs_number': fields.text('NHS Number'),
        'state': fields.selection(_state_selection, 'State'),
    }

    def init(self, cr):

        cr.execute("""
                drop view if exists %s;
                create or replace view %s as (
                    select
                        spell_activity.id as id,
                        referral_activity.id as activity_id,
                        referral_activity.pos_id as pos_id,
                        case
                            when discharge_activity.state is not null and discharge_activity.state = 'completed' then 'Done'
                            when clerking_activity.state is not null and clerking_activity.state != 'scheduled' then 'Done'
                            when referral_activity.state = 'scheduled' then 'Referral'
                            else 'To be Clerked'
                        end as state,
                        spell.patient_id as patient_id,
                        referral_activity.location_id as location_id,
                        patient.other_identifier as hospital_number,
                        patient.patient_identifier as nhs_number
                    from nh_clinical_spell spell
                    inner join nh_activity spell_activity on spell_activity.id = spell.activity_id
                    inner join nh_clinical_patient patient on spell.patient_id = patient.id
                    inner join nh_activity referral_activity on referral_activity.parent_id = spell_activity.id and referral_activity.data_model = 'nh.clinical.patient.referral' and referral_activity.state in ('scheduled','completed')
                    left join nh_activity discharge_activity on discharge_activity.parent_id = spell_activity.id and discharge_activity.data_model = 'nh.clinical.adt.patient.discharge'
                    left join nh_activity clerking_activity on clerking_activity.parent_id = spell_activity.id and clerking_activity.data_model = 'nh.clinical.patient.clerking'
                    left join nh_clinical_location location on location.id = spell.location_id
                )
        """ % (self._table, self._table))

    def _get_referral_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        res = [['Referral', 'Referral'], ['To be Clerked', 'To be Clerked']]
        fold = {r[0]: False for r in res}
        return res, fold

    _group_by_full = {
        'state': _get_referral_groups,
    }

    def complete(self, cr, uid, ids, context=None):
        referral = self.browse(cr, uid, ids[0], context=context)

        activity_pool = self.pool['nh.activity']
        activity_pool.complete(cr, uid, referral.activity_id.id, context=context)

        act_window_pool = self.pool['ir.actions.act_window']
        action_id = act_window_pool.search(cr, SUPERUSER_ID, [['name', '=', 'Patient Referrals']], context=context)
        action = act_window_pool.browse(cr, SUPERUSER_ID, action_id[0], context=context)

        return {
            'name': action.name,
            'res_model': action.res_model,
            'type': 'ir.actions.act_window',
            'view_type': action.view_type,
            'domain': action.domain,
            'view_mode': 'tree,form'
        }