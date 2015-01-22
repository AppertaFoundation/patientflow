from openerp.osv import orm, fields
from openerp.addons.nh_activity.activity import except_if
from openerp import SUPERUSER_ID


class nh_clinical_patient_referral(orm.Model):
    """
    Represents external patient referrals that are entered into the system but the patients have not arrived yet to the specified location.
    * Usually handled by receptionist users.
    * Whenever it's completed means that the patient has arrived and it is moved to the specified location.
    """
    _name = 'nh.clinical.patient.referral'
    _inherit = ['nh.activity.data']
    _description = "Patient Referral"
    _start_view_xmlid = "view_patient_referral_form"
    _schedule_view_xmlid = "view_patient_referral_form"
    _submit_view_xmlid = "view_patient_referral_form"
    _complete_view_xmlid = "view_patient_referral_complete"
    _cancel_view_xmlid = "view_patient_referral_form"

    _columns = {
        'location_id': fields.many2one('nh.clinical.location', 'Destination Location'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
        'pos_id': fields.related('activity_id', 'pos_id', type='many2one', relation='nh.clinical.pos', string='POS'),
    }

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        return activity.data_ref.location_id.id

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        move_pool = self.pool['nh.clinical.patient.move']
        referral_activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not referral_activity.data_ref.location_id,
                  msg="Location is not set, referral can't be completed! activity.id = %s" % referral_activity.id)
        res = super(nh_clinical_patient_referral, self).complete(cr, uid, activity_id, context)

        referral_activity = activity_pool.browse(cr, uid, activity_id, context)
        # set spell location
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, referral_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id,
                  cap="Spell in state 'started' is not found for patient_id=%s" % referral_activity.data_ref.patient_id.id,
                  msg="Referral can not be completed")
        # move to location
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                                                    {'parent_id': spell_activity_id,
                                                     'creator_id': activity_id},
                                                    {'patient_id': referral_activity.data_ref.patient_id.id,
                                                     'location_id': referral_activity.data_ref.location_id.id})
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id)
        activity_pool.submit(cr, SUPERUSER_ID, spell_activity_id, {'location_id': referral_activity.data_ref.location_id.id})
        # trigger referral policy activities
        self.trigger_policy(cr, uid, activity_id, location_id=referral_activity.data_ref.location_id.id, context=context)
        return res


class nh_clinical_patient_referral_form(orm.Model):
    _name = 'nh.clinical.patient.referral.form'
    _description = "Patient Referral Form"
    _boolean = [['yes', 'Yes'], ['no', 'No']]
    _boolean2 = [['yes', 'Yes'], ['no', 'No'], ['na', 'N/A']]
    _referral_source = [['gp', 'GP'], ['ucc', 'UCC'], ['ae', 'A&E'], ['eau', 'EAU'], ['ecp', 'ECP'], ['wic', 'WIC'],
                        ['ltxc', 'LTxC'], ['opd', 'OPD'], ['mac', 'MAC'], ['comm', 'COMM'], ['matron', 'MATRON'],
                        ['hospice', 'HOSPICE'], ['cons', 'CONS']]
    _gender = [['M', 'Male'], ['F', 'Female']]
    _resides = [['home', 'HOME'], ['res', 'RES/HOME'], ['nursing', 'N/HOME']]
    _advised_attendance = [['ae', 'A&E'], ['eau', 'EAU'], ['acc', 'ACC'], ['clinic', 'CLINIC']]
    _poc = [['eau', 'EAU'], ['ae', 'A&E'], ['acc', 'ACC'], ['smdu', 'SMDU'], ['clinic', 'Clinic']]
    _averted = [['com', 'Community'], ['clinic', 'Clinic'], ['ae', 'A&E'], ['eau', 'EAU'], ['acu', 'ACU'],
                ['mobile', 'Mobile']]
    _ethnicity = [['w_b', 'White British'], ['w_i', 'White Irish'], ['w_o', 'White Other'], ['o', 'Other']]

    _columns = {
        # system data
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Write Date', readonly=True),
        'create_uid': fields.many2one('res.users', 'Created By', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated By', readonly=True),

        'source': fields.selection(_referral_source, 'Source of Referral'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'nhs_number': fields.char('NHS Number', size=50),
        'first_name': fields.char('First Name', size=50),
        'middle_names': fields.char('Middle Names', size=100),
        'last_name': fields.char('Last Name', size=50),
        'dob': fields.datetime('Date of Birth'),
        'postcode': fields.char('Postcode', size=10),  # Patient or GP/Surgery?
        'ref_doctor_id': fields.many2one('res.partner', 'Referring Doctor', domain=[['doctor', '=', True]]),  # GP/Surgery
        'ethnicity': fields.selection(_ethnicity, 'Ethnicity'),
        'gender': fields.selection(_gender, 'Gender'),
        'resides': fields.selection(_resides, 'Resides'),
        'symptoms_notes': fields.text('Symptoms/Investigations Treatment'),
        'infection_concerns': fields.char('Infection Concerns?', size=200),
        'body_temperature': fields.float('Body Temperature', digits=(2, 1)),
        'pulse_rate': fields.integer('Pulse Rate'),
        'blood_pressure_systolic': fields.integer('Blood Pressure Systolic'),
        'blood_pressure_diastolic': fields.integer('Blood Pressure Diastolic'),
        'o2_saturation': fields.integer('O2 Saturation'),
        'weight': fields.float('Weight', digits=(3, 1)),
        'medical_history_notes': fields.text('Past Medical History'),
        'allergies': fields.text('Allergies'),
        'access_clinic_datetime': fields.datetime('Emergency GP Access Clinic Date & Time'),
        'referral_reason': fields.char('Reason for referral', size=200),
        'medication_list': fields.selection(_boolean, 'Medication List Requested'),
        'diagnosis': fields.char('Possible diagnosis', size=200),
        'speciality': fields.char('Speciality', size=200),
        'advised_attendance': fields.selection(_advised_attendance, 'Advised Attendance At'),
        'environmental_factors': fields.text('Environmental Factors, Social/Family'),
        'elsewhere_treatment': fields.selection(_boolean, 'Can patient be treated elsewhere?'),
        'letter_request': fields.boolean('Letter Requested'),
        'ambulance': fields.boolean('Ambulance'),
        'gp_options_discussed': fields.selection(_boolean2, 'If yes were options discussed with GP?'),
        'gp_options_choice': fields.selection(_boolean, 'Did the GP choose any other option?'),
        'eau_informed': fields.selection(_boolean, 'EAU Informed'),
        'acc_informed': fields.selection(_boolean, 'ACC Informed'),
        'team_informed': fields.selection(_boolean, 'Team Informed'),
        'poc': fields.selection(_poc, 'First Point of Contact'),
        'averted': fields.selection(_averted, 'Averted in'),
    }

    _defaults = {
        'source': 'gp'
    }

    def onchange_patient_id(self, cr, uid, ids, patient_id, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        if not patient_id:
            return {}
        patient = patient_pool.browse(cr, uid, patient_id, context=context)
        return {
            'value': {
                'nhs_number': patient.patient_identifier,
                'first_name': patient.given_name,
                'middle_names': patient.middle_names,
                'last_name': patient.family_name,
                'dob': patient.dob,
                'gender': patient.gender if patient.gender in [g[0] for g in self._gender] else False,
                'ethnicity': patient.ethnicity if patient.ethnicity in [e[0] for e in self._ethnicity] else False,
            }
        }