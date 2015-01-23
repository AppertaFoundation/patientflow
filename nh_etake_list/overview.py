from openerp.osv import orm, fields
import logging
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)


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
                        ['Clerking in Process', 'Clerking in Process'],
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
                        tci_activity.id as activity_id,
                        tci_activity.pos_id as pos_id,
                        case
                            when spell_activity.state = 'completed' or spell_activity.state = 'cancelled' then 'Done'
                            when discharge_activity.state is not null and discharge_activity.state = 'completed' then 'Done'
                            when discharge_activity.state is not null and discharge_activity.state != 'completed' then 'To be Discharged'
                            when referral_activity.state is not null and referral_activity.state = 'scheduled' then 'Referral'
                            when tci_activity.state is not null and tci_activity.state = 'scheduled' then 'TCI'
                            when clerking_activity.state = 'scheduled' then 'To be Clerked'
                            when clerking_activity.state = 'started' then 'Clerking in Process'
                            when ptwr_activity.state is not null then 'Consultant Review'
                            when review_activity.state = 'scheduled' then 'Senior Review'
                            else 'Other'
                        end as state,
                        spell.patient_id as patient_id,
                        case
                            when tci_activity.state = 'scheduled' then tci_activity.location_id
                            else location.id
                        end as location_id,
                        patient.other_identifier as hospital_number,
                        patient.patient_identifier as nhs_number
                    from nh_clinical_spell spell
                    inner join nh_activity spell_activity on spell_activity.id = spell.activity_id
                    inner join nh_clinical_patient patient on spell.patient_id = patient.id
                    left join nh_activity referral_activity on referral_activity.parent_id = spell_activity.id and referral_activity.data_model = 'nh.clinical.patient.referral'
                    left join nh_activity tci_activity on tci_activity.parent_id = spell_activity.id and tci_activity.data_model = 'nh.clinical.patient.tci'
                    left join nh_activity discharge_activity on discharge_activity.parent_id = spell_activity.id and discharge_activity.data_model = 'nh.clinical.adt.patient.discharge'
                    left join nh_activity clerking_activity on clerking_activity.parent_id = spell_activity.id and clerking_activity.data_model = 'nh.clinical.patient.clerking'
                    left join nh_activity review_activity on review_activity.parent_id = spell_activity.id and review_activity.data_model = 'nh.clinical.patient.review'
                    left join nh_activity ptwr_activity on ptwr_activity.parent_id = spell_activity.id and ptwr_activity.data_model = 'nh.clinical.ptwr' and ptwr_activity.state != 'completed'
                    left join nh_clinical_location location on location.id = spell.location_id
                    where referral_activity.id is not null or tci_activity.id is not null
                )
        """ % (self._table, self._table))

    def _get_overview_groups(self, cr, uid, ids, domain, read_group_order=None, access_rights_uid=None, context=None):
        res = [
            ['Referral', 'Referral'],
            ['TCI', 'To Come In'],
            ['To be Clerked', 'To be Clerked'],
            ['Clerking in Process', 'Clerking in Process'],
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