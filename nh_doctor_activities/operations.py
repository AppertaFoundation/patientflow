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


class nh_clinical_doctor_task(orm.Model):
    """
    Represents patient review done by doctors.
    * Usually handled by senior doctors.
    """
    _name = 'nh.clinical.doctor.task'
    _inherit = ['nh.activity.data']
    _description = "Doctor Task"