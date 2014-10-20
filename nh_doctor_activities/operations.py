from openerp.osv import orm, fields
from openerp.addons.nh_activity.activity import except_if
from openerp import SUPERUSER_ID


class nh_clinical_patient_clerking(orm.Model):
    """
    Represents initial assessment done by doctors.
    * Usually handled by junior doctors.
    """
    _name = 'nh.clinical.patient.clerking'
    _inherit = ['nh.activity.data']
    _description = "Patient Clerking"

    _columns = {
        'patient_id': fields.related('activity_id', 'patient_id', string='Patient', type='many2one', relation='nh.clinical.patient')
    }

    def complete(self, cr, uid, activity_id, context=None):
        activity_pool = self.pool['nh.activity']
        res = super(nh_clinical_patient_clerking, self).complete(cr, uid, activity_id, context)
        clerking_activity = activity_pool.browse(cr, uid, activity_id, context=context)
        # trigger referral policy activities
        self.trigger_policy(cr, uid, activity_id, location_id=clerking_activity.location_id.id, context=context)
        return res


class nh_clinical_patient_review(orm.Model):
    """
    Represents patient review done by doctors.
    * Usually handled by senior doctors.
    """
    _name = 'nh.clinical.patient.review'
    _inherit = ['nh.activity.data']
    _description = "Patient Review"

    _columns = {
        'patient_id': fields.related('activity_id', 'patient_id', string='Patient', type='many2one', relation='nh.clinical.patient'),
        'location_id': fields.many2one('nh.clinical.location', 'Patient reviewed in this location')
    }


class nh_clinical_doctor_task(orm.Model):
    """
    Represents patient review done by doctors.
    * Usually handled by senior doctors.
    """
    _name = 'nh.clinical.doctor.task'
    _inherit = ['nh.activity.data']
    _description = "Doctor Task"

    _columns = {
        'patient_id': fields.related('activity_id', 'patient_id', string='Patient', type='many2one', relation='nh.clinical.patient')
    }


class nh_clinical_ptwr(orm.Model):
    """
    Represents PTWR tasks done by doctors.
    * Usually handled by consultants.
    """
    _name = 'nh.clinical.ptwr'
    _inherit = ['nh.activity.data']
    _description = "PTWR"

    _columns = {
        'patient_id': fields.related('activity_id', 'patient_id', string='Patient', type='many2one', relation='nh.clinical.patient')
    }