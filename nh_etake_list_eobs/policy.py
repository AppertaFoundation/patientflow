from openerp.osv import orm


class nh_clinical_patient_admission(orm.Model):
    _name = 'nh.clinical.patient.admission'
    _inherit = 'nh.clinical.patient.admission'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.suggested_location_id.id'
                               }},
                              {'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'create_data': {
                                   'location_id': 'activity.data_ref.suggested_location_id.id'
                               }}]}


class nh_clinical_adt_patient_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.transfer'
    _inherit = 'nh.clinical.adt.patient.transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.location_id.id'
                               }
                              },
                              {'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'cancel_others': False,
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


class nh_clinical_adt_spell_update(orm.Model):
    _name = 'nh.clinical.adt.spell.update'
    _inherit = 'nh.clinical.adt.spell.update'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.suggested_location_id.id'
                               }
                              },
                              {'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'cancel_others': False,
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
                                   'location_id': 'activity.data_ref.suggested_location_id.id'
                               }
                              }]}


class nh_clinical_adt_patient_cancel_discharge(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_discharge'
    _inherit = 'nh.clinical.adt.patient.cancel_discharge'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id':
                                       "location_pool.get_closest_parent_id(cr, uid, 'ward', "
                                       "activity.data_ref.last_location_id.id, context=context) if "
                                       "activity.data_ref.last_location_id.usage != 'ward' else "
                                       "activity.data_ref.last_location_id.id"
                               }
                               }]}


class nh_clinical_adt_patient_cancel_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_transfer'
    _inherit = 'nh.clinical.adt.patient.cancel_transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.placement',
                               'type': 'schedule',
                               'context': 'eobs',
                               'cancel_others': True,
                               'create_data': {
                                   'suggested_location_id': 'activity.data_ref.last_location_id.id'
                               }
                               },
                              {'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'cancel_others': False,
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
                                   'location_id': 'activity.data_ref.last_location_id.id'
                               }
                               }]}
