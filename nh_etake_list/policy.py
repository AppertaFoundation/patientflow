from openerp.osv import orm


class nh_clinical_patient_referral(orm.Model):
    _name = 'nh.clinical.patient.referral'
    _inherit = 'nh.clinical.patient.referral'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'create_data': {
                                   'location_id': 'activity.data_ref.tci_location_id.id'
                               }}]}


class nh_clinical_patient_tci(orm.Model):
    _name = 'nh.clinical.patient.tci'
    _inherit = 'nh.clinical.patient.tci'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.clerking',
                               'type': 'schedule',
                               'context': 'etakelist'}]}


class nh_clinical_patient_clerking(orm.Model):
    _name = 'nh.clinical.patient.clerking'
    _inherit = 'nh.clinical.patient.clerking'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.review',
                               'type': 'schedule',
                               'context': 'etakelist'}]}


class nh_clinical_patient_admission(orm.Model):
    _name = 'nh.clinical.patient.admission'
    _inherit = 'nh.clinical.patient.admission'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'create_data': {
                                   'location_id': 'activity.data_ref.location_id.id'
                               }}]}


class nh_clinical_patient_transfer(orm.Model):
    _name = 'nh.clinical.patient.transfer'
    _inherit = 'nh.clinical.patient.transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule', 
                               'context': 'etakelist',
                               'domains': [
                                   {
                                       'object': 'nh.activity',
                                       'domain': [['data_model', 'in', ['nh.clinical.patient.tci',
                                                                        'nh.clinical.adt.patient.discharge',
                                                                        'nh.clinical.patient.clerking',
                                                                        'nh.clinical.ptwr']],
                                                  ['state', 'not in', ['completed', 'cancelled']]]
                                   }
                               ],
                               'cancel_others': True,
                               'create_data': {
                                   'location_id': 'activity.data_ref.location_id.id'
                               },
                               'case': 1
                              }, {'model': 'nh.clinical.patient.tci',
                                 'type': 'schedule',
                                 'context': 'etakelist',
                                 'domains': [
                                       {
                                           'object': 'nh.activity',
                                           'domain': [['data_model', 'in', ['nh.clinical.patient.tci',
                                                                            'nh.clinical.adt.patient.discharge',
                                                                            'nh.clinical.patient.clerking',
                                                                            'nh.clinical.ptwr']],
                                                      ['state', 'not in', ['completed', 'cancelled']]]
                                       }
                                   ],
                                 'cancel_others': True,
                                 'create_data': {
                                    'location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.origin_loc_id.id, context=context) if "
                                       "activity.data_ref.origin_loc_id.usage != 'ward' else "
                                       "activity.data_ref.origin_loc_id.id"
                                 },
                                 'case': 2
                                 }]}
    
    
class nh_clinical_adt_spell_update(orm.Model):
    _name = 'nh.clinical.adt.spell.update'
    _inherit = 'nh.clinical.adt.spell.update'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule', 
                               'context': 'etakelist',
                               'cancel_others': True,
                               'domains': [
                                   {
                                       'object': 'nh.activity',
                                       'domain': [['data_model', 'in', ['nh.clinical.patient.tci',
                                                                        'nh.clinical.adt.patient.discharge',
                                                                        'nh.clinical.patient.clerking',
                                                                        'nh.clinical.ptwr']],
                                                  ['state', 'not in', ['completed', 'cancelled']]]
                                   }
                               ],
                               'create_data': {
                                   'location_id': 'activity.data_ref.location_id.id'
                               }
                               }]}
    

class nh_clinical_patient_discharge(orm.Model):
    _name = 'nh.clinical.patient.discharge'
    _inherit = 'nh.clinical.patient.discharge'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule', 
                               'context': 'etakelist',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.last_location_id.id, context=context) if "
                                       "activity.data_ref.last_location_id.usage != 'ward' else "
                                       "activity.data_ref.last_location_id.id"
                               }
                               }]}