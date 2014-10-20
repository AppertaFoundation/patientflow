from openerp.osv import orm, fields
import logging

_logger = logging.getLogger(__name__)


class nh_etake_list_referral(orm.Model):
    _name = "nh.etake_list.referral"
    _inherits = {'nh.activity': 'activity_id'}
    _description = "Referral View"
    _rec_name = 'patient_id'
    _auto = False
    _table = "nh_etake_list_referral"
    _columns = {
        'activity_id': fields.many2one('nh.activity', 'Activity', required=1, ondelete='restrict'),
        'location_id': fields.many2one('nh.clinical.location', 'Ward'),
        'pos_id': fields.many2one('nh.clinical.pos', 'POS'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'hospital_number': fields.text('Hospital Number')
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
                        activity.pos_id as pos_id,
                        patient.other_identifier as hospital_number
                    from nh_activity activity
                    inner join nh_clinical_patient patient on activity.patient_id = patient.id
                    where activity.data_model = 'nh.clinical.patient.referral' and activity.state not in ('completed','cancelled')
                )
        """ % (self._table, self._table))

    def complete(self, cr, uid, ids, context=None):
        referral = self.browse(cr, uid, ids[0], context=context)

        model_data_pool = self.pool['ir.model.data']
        model_data_ids = model_data_pool.search(cr, uid, [('name', '=', 'view_patient_referral_complete')], context=context)
        if not model_data_ids:
            pass # view doesnt exist
        view_id = model_data_pool.read(cr, uid, model_data_ids, ['res_id'], context)[0]['res_id']

        return {
            'name': 'Patient On Site',
            'type': 'ir.actions.act_window',
            'res_model': 'nh.clinical.patient.referral',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': referral.activity_id.data_ref.id,
            'target': 'new',
            'view_id': int(view_id),
            'context': context
        }