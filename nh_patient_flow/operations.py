from openerp.osv import orm, fields, osv
from openerp.addons.nh_activity.activity import except_if
from openerp import SUPERUSER_ID
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf


class nh_clinical_patient_tci(orm.Model):
    """
    Represents external patients to come in the hospital but the patients have not arrived yet to the specified location.
    * Usually handled by receptionist users.
    * Whenever it's completed means that the patient has arrived and it is moved to the specified location.
    """
    _name = 'nh.clinical.patient.tci'
    _inherit = ['nh.activity.data']
    _description = "Patient To Come In"
    _complete_view_xmlid = "view_patient_tci_complete"

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
        tci_activity = activity_pool.browse(cr, uid, activity_id, context)
        except_if(not tci_activity.data_ref.location_id,
                  msg="Location is not set, referral can't be completed! activity.id = %s" % tci_activity.id)
        res = super(nh_clinical_patient_tci, self).complete(cr, uid, activity_id, context)

        tci_activity = activity_pool.browse(cr, uid, activity_id, context)
        # set spell location
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, tci_activity.data_ref.patient_id.id, context=context)
        except_if(not spell_activity_id,
                  cap="Spell in state 'started' is not found for patient_id=%s" % tci_activity.data_ref.patient_id.id,
                  msg="Referral can not be completed")
        # move to location
        move_activity_id = move_pool.create_activity(cr, SUPERUSER_ID,
                                                    {'parent_id': spell_activity_id,
                                                     'creator_id': activity_id},
                                                    {'patient_id': tci_activity.data_ref.patient_id.id,
                                                     'location_id': tci_activity.data_ref.location_id.id})
        activity_pool.complete(cr, SUPERUSER_ID, move_activity_id)
        activity_pool.submit(cr, SUPERUSER_ID, spell_activity_id, {'location_id': tci_activity.data_ref.location_id.id})
        # trigger tci policy activities
        self.trigger_policy(cr, uid, activity_id, location_id=tci_activity.data_ref.location_id.id, context=context)
        return res


class nh_clinical_patient_referral_form(orm.Model):
    _name = 'nh.clinical.patient.referral.form'
    _description = "Patient Referral Form"
    _rec_name = 'patient_id'
    _boolean = [['yes', 'Yes'], ['no', 'No']]
    _boolean2 = [['yes', 'Yes'], ['no', 'No'], ['na', 'N/A']]
    _referral_source = [['gp', 'GP'], ['ucc', 'UCC'], ['ae', 'A&E'], ['eau', 'EAU'], ['ecp', 'ECP'], ['wic', 'WIC'],
                        ['ltxc', 'LTxC'], ['opd', 'OPD'], ['mac', 'MAC'], ['comm', 'COMM'], ['matron', 'MATRON'],
                        ['hospice', 'HOSPICE'], ['cons', 'CONS']]
    _resides = [['home', 'HOME'], ['res', 'RES/HOME'], ['nursing', 'N/HOME']]
    _advised_attendance = [['ae', 'A&E'], ['eau', 'EAU'], ['acc', 'ACC'], ['clinic', 'CLINIC']]
    _poc = [['eau', 'EAU'], ['ae', 'A&E'], ['acc', 'ACC'], ['smdu', 'SMDU'], ['clinic', 'Clinic']]
    _averted = [['com', 'Community'], ['clinic', 'Clinic'], ['ae', 'A&E'], ['eau', 'EAU'], ['acu', 'ACU'],
                ['mobile', 'Mobile']]
    _ethnicity = [
        ['A', 'White - British'], ['B', 'White - Irish'], ['C', 'White - Other background'],
        ['D', 'Mixed - White and Black Caribbean'], ['E', 'Mixed - White and Black African'],
        ['F', 'Mixed - White and Asian'], ['G', 'Mixed - Other background'], ['H', 'Asian - Indian'],
        ['J', 'Asian - Pakistani'], ['K', 'Asian - Bangladeshi'], ['L', 'Asian - Other background'],
        ['M', 'Black - Caribbean'], ['N', 'Black - African'], ['P', 'Black - Other background'], ['R', 'Chinese'],
        ['S', 'Other ethnic group'], ['Z', 'Not stated']
    ]
    _gender = [['BOTH', 'Both'], ['F', 'Female'], ['I', 'Intermediate'],
               ['M', 'Male'], ['NSP', 'Not Specified'], ['U', 'Unknown']]
    _patient_values = ['patient_id', 'hospital_number', 'nhs_number', 'first_name', 'middle_names', 'last_name', 'dob',
                       'ethnicity', 'gender']

    _columns = {
        # system data
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Write Date', readonly=True),
        'create_uid': fields.many2one('res.users', 'Created By', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated By', readonly=True),

        'source': fields.selection(_referral_source, 'Source of Referral'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'nhs_number': fields.char('NHS Number', size=50),
        'hospital_number': fields.char('Hospital Number', size=50),
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
        'specialty': fields.many2one('nh.clinical.specialty', 'Specialty'),
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
        'source': 'gp',
        'ethnicity': 'Z',
        'gender': 'NSP'
    }

    def _check_patient_values(self, cr, uid, vals, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        patient_vals = {
            'other_identifier': vals.get('hospital_number'),
            'patient_identifier': vals.get('nhs_number'),
            'given_name': vals.get('first_name'),
            'middle_names': vals.get('middle_names'),
            'family_name': vals.get('last_name'),
            'dob': vals.get('dob'),
            'gender': vals.get('gender'),
            'ethnicity': vals.get('ethnicity')
        }
        if vals.get('patient_id'):
            match = patient_pool._check_match(cr, uid, vals.get('patient_id'), patient_vals, context=context)
            if not match:
                raise osv.except_osv('Error!', "Cannot submit form. The values in the form do not match the selected patient data")
            else:
                return vals.get('patient_id')
        if vals.get('hospital_number'):
            patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', vals.get('hospital_number')]], context=context)
            if patient_id:
                match = patient_pool._check_match(cr, uid, patient_id[0], patient_vals, context=context)
                if not match:
                    raise osv.except_osv('Error!', "Cannot submit form. There is already a patient in the system with that hospital number and the data does not match.")
                else:
                    return patient_id[0]
        if vals.get('nhs_number'):
            patient_id = patient_pool.search(cr, uid, ['|',
                                                   ['patient_identifier', '=', vals.get('nhs_number')],
                                                   ['unverified_nhs', '=', vals.get('nhs_number')]], context=context)
            if patient_id:
                match = patient_pool._check_match(cr, uid, patient_id[0], patient_vals, context=context)
                if not match:
                    raise osv.except_osv('Error!', "Cannot submit form. There is already a patient in the system with that NHS number and the data does not match.")
                else:
                    return patient_id[0]
        return False

    def create(self, cr, uid, vals, context=None):
        form_id = super(nh_clinical_patient_referral_form, self).create(cr, uid, vals, context=context)
        patient_id = self._check_patient_values(cr, uid, vals, context=context)
        if not patient_id:
            patient_pool = self.pool['nh.clinical.patient']
            patient_vals = {
                'other_identifier': 'NH_'+str(form_id) if not vals.get('hospital_number') else vals.get('hospital_number'),
                'unverified_nhs': vals.get('nhs_number'),
                'given_name': vals.get('first_name'),
                'middle_names': vals.get('middle_names'),
                'family_name': vals.get('last_name'),
                'dob': vals.get('dob'),
                'gender': vals.get('gender') if vals.get('gender') else 'NSP',
                'ethnicity': vals.get('ethnicity') if vals.get('ethnicity') else 'Z'
            }
            patient_id = patient_pool.create(cr, uid, patient_vals, context=context)
            self.write(cr, uid, form_id, {'patient_id': patient_id}, context=context)
        # create referral
        self.pool['nh.clinical.patient.referral'].create_activity(cr, SUPERUSER_ID, {
            'patient_id': patient_id,
        }, {'form_id': form_id, 'patient_id': patient_id}, context=context)
        return form_id

    def write(self, cr, uid, ids, vals, context=None):
        res = super(nh_clinical_patient_referral_form, self).write(cr, uid, ids, vals, context=context)
        # if any([k in self._patient_values for k in vals.keys()]):
        #     update_vals = {}
        #     for k in vals.keys():
        #         if k in self._patient_values:
        #             update_vals[k] = vals[k]
        #     for form in self.browse(cr, uid, ids, context=context):
        #         self.pool['nh.clinical.patient'].write(cr, uid, form.patient_id.id, update_vals, context=context)
        return res

    def onchange_patient_id(self, cr, uid, ids, patient_id, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        if not patient_id:
            return {}
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

    def onchange_nhs_number(self, cr, uid, ids, nhs_number, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        clear_patient_id = {
            'value': {
                'patient_id': False,
            }
        }
        if not nhs_number:
            return clear_patient_id
        patient_id = patient_pool.search(cr, uid, ['|',
                                                   ['patient_identifier', '=', nhs_number],
                                                   ['unverified_nhs', '=', nhs_number]], context=context)
        if not patient_id:
            return clear_patient_id
        patient = patient_pool.browse(cr, uid, patient_id[0], context=context)
        return {
            'value': {
                'patient_id': patient_id[0],
                'hospital_number': patient.other_identifier,
                'first_name': patient.given_name,
                'middle_names': patient.middle_names,
                'last_name': patient.family_name,
                'dob': patient.dob,
                'gender': patient.gender if patient.gender in [g[0] for g in self._gender] else False,
                'ethnicity': patient.ethnicity if patient.ethnicity in [e[0] for e in self._ethnicity] else False,
            }
        }

    def onchange_hospital_number(self, cr, uid, ids, hospital_number, context=None):
        patient_pool = self.pool['nh.clinical.patient']
        clear_patient_id = {
            'value': {
                'patient_id': False,
            }
        }
        if not hospital_number:
            return clear_patient_id
        patient_id = patient_pool.search(cr, uid, [['other_identifier', '=', hospital_number]], context=context)
        if not patient_id:
            return clear_patient_id
        patient = patient_pool.browse(cr, uid, patient_id[0], context=context)
        return {
            'value': {
                'patient_id': patient_id[0],
                'nhs_number': patient.patient_identifier if patient.patient_identifier else patient.unverified_nhs,
                'first_name': patient.given_name,
                'middle_names': patient.middle_names,
                'last_name': patient.family_name,
                'dob': patient.dob,
                'gender': patient.gender if patient.gender in [g[0] for g in self._gender] else False,
                'ethnicity': patient.ethnicity if patient.ethnicity in [e[0] for e in self._ethnicity] else False,
            }
        }


class nh_clinical_patient_referral(orm.Model):
    _name = 'nh.clinical.patient.referral'
    _inherit = ['nh.activity.data']
    _description = "Patient Referral"

    _columns = {
        'form_id': fields.many2one('nh.clinical.patient.referral.form', 'Referral Form'),
        'tci_location_id': fields.many2one('nh.clinical.location', 'To Come In Location'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient', required=True),
    }

    def get_activity_location_id(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        activity = activity_pool.browse(cr, uid, activity_id, context)
        return activity.data_ref.tci_location_id.id

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        api_pool = self.pool['nh.clinical.api']
        res = super(nh_clinical_patient_referral, self).complete(cr, uid, activity_id, context)
        referral = activity_pool.browse(cr, SUPERUSER_ID, activity_id, context=context)
        spell_activity_id = api_pool.get_patient_spell_activity_id(cr, SUPERUSER_ID, referral.patient_id.id, context=context)
        if not spell_activity_id:
            spell_pool = self.pool['nh.clinical.spell']
            spell_activity_id = spell_pool.create_activity(cr, SUPERUSER_ID, {'creator_id': activity_id},
                                                           {'patient_id': referral.patient_id.id,
                                                            'location_id': referral.data_ref.tci_location_id.id,
                                                            'pos_id': referral.data_ref.tci_location_id.pos_id.id,
                                                            'start_date': dt.now().strftime(dtf)}, context=context)
            activity_pool.start(cr, SUPERUSER_ID, spell_activity_id, context=context)
        # trigger referral policy activities
        self.trigger_policy(cr, uid, activity_id, context=context)
        return res