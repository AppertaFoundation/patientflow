from openerp.osv import orm, fields


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

    def _check_nhs_number(self, cr, uid, nhs_number, data, context=None):
        if not nhs_number:
            return False
        domain = [('patient_identifier', '=', nhs_number)]
        patient_id = self.search(cr, uid, domain, context=context)
        if patient_id:
            return self.write(cr, uid, patient_id[0], data, context=context)
        else:
            domain = [('unverified_nhs', '=', nhs_number)]
            patient_id = self.search(cr, uid, domain, context=context)
            if patient_id:
                match = self._check_match(cr, uid, patient_id[0], data, context=context)
                if match:
                    self.write(cr, uid, patient_id[0], {'patient_identifier': nhs_number}, context=context)
                    return self.write(cr, uid, patient_id[0], data, context=context)
        return False