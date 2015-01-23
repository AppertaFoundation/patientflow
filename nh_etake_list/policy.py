from openerp.osv import orm


class nh_clinical_patient_referral(orm.Model):
    _name = 'nh.clinical.patient.referral'
    _inherit = 'nh.clinical.patient.referral'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule',
                               'context': 'etakelist',
                               'create_data': {
                                   'location_id': 'data_ref.tci_location_id.id'
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
                                   'location_id': 'data_ref.suggested_location_id.id'
                               }}]}


class nh_clinical_adt_patient_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.transfer'
    _inherit = 'nh.clinical.adt.patient.transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule', 
                               'context': 'etakelist',
                               'cancel_others': True,
                               'create_data': {
                                   'location_id': 'data_ref.location_id.id'
                               }
                              }]}
    
    
class nh_clinical_adt_spell_update(orm.Model):
    _name = 'nh.clinical.adt.spell.update'
    _inherit = 'nh.clinical.adt.spell.update'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule', 
                               'context': 'etakelist',
                               'cancel_others': True,
                               'create_data': {
                                   'location_id': 'data_ref.suggested_location_id.id'
                               }
                              }]}
    

class nh_clinical_adt_patient_cancel_discharge(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_discharge'
    _inherit = 'nh.clinical.adt.patient.cancel_discharge'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule', 
                               'context': 'etakelist',
                               'cancel_others': True,
                               'create_data': {
                                   'location_id': 'data_ref.last_location_id.parent_id.id'
                               }
                              }]}


class nh_clinical_adt_patient_cancel_transfer(orm.Model):
    _name = 'nh.clinical.adt.patient.cancel_transfer'
    _inherit = 'nh.clinical.adt.patient.cancel_transfer'

    _POLICY = {'activities': [{'model': 'nh.clinical.patient.tci',
                               'type': 'schedule', 
                               'context': 'etakelist',
                               'cancel_others': True,
                               'create_data': {
                                   'location_id': 'data_ref.last_location_id.id'
                               }
                              }]}