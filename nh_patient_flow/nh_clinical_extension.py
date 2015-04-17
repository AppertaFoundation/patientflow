from openerp.osv import orm, fields, osv


class nh_clinical_patient_flow_patient(orm.Model):
    _name = 'nh.clinical.patient'
    _inherit = 'nh.clinical.patient'

    _columns = {
        'unverified_nhs': fields.char('NHS Number', size=100)
    }
    
    def _check_match(self, cr, uid, patient_id, data, context=None):
        patient = self.browse(cr, uid, patient_id, context=context)
        keys = ['given_name', 'middle_names', 'family_name', 'dob', 'gender', 'ethnicity', 'other_identifier']
        for k in keys:
            if eval('patient.%s' % k) and data.get(k):
                if k not in ('gender', 'ethnicity', 'other_identifier'):
                    if eval('patient.%s' % k) != data.get(k):
                        return False
                elif k == 'other_identifier':
                    if eval('patient.%s' % k) != data.get(k) and eval('patient.%s' % k)[0:3] != 'NH_':
                        return False
                elif k == 'gender':
                    if eval('patient.%s' % k) != data.get(k) and eval('patient.%s' % k) != 'NSP':
                        return False
                else:
                    if eval('patient.%s' % k) != data.get(k) and eval('patient.%s' % k) != 'Z':
                        return False
        patient_nhs = patient.patient_identifier or patient.unverified_nhs
        data_nhs = data.get('patient_identifier') or data.get('unverified_nhs')
        if patient_nhs and data_nhs:
            if patient_nhs != data_nhs:
                return False
        return True

    def check_nhs_number(self, cr, uid, nhs_number, exception=False, context=None):
        """
        Checks if there is a patient with the provided NHS Number
        If there is no patient with the provided NHS Number and a patient with a matching unverified NHS number is
        found, its actual NHS Number will be updated.
        :param exception: string with values 'True' or 'False'.
        :return: if no exception parameter is provided: True if patient exists. False if not.
                if exception = 'True': Integrity Error exception is raised if patient exists. False if not.
                if exception = 'False': True if patient exists. Patient Not Found exception is raised if not.
        """
        domain = [['patient_identifier', '=', nhs_number]]
        result = bool(self.search(cr, uid, domain, context=context))
        if not result:
            domain = [['unverified_nhs', '=', nhs_number]]
            patient_id = self.search(cr, uid, domain, context=context)
            if patient_id:
                self.write(cr, uid, patient_id, {'patient_identifier': nhs_number}, context=context)
            result = bool(patient_id)
        if exception:
            if eval(exception) and result:
                raise osv.except_osv('Integrity Error!', 'Patient with NHS Number %s already exists!'
                                     % nhs_number)
            elif not eval(exception) and not result:
                raise osv.except_osv('Patient Not Found!', 'There is no patient with NHS Number %s' %
                                     nhs_number)
        return result