from openerp.osv import osv, fields
from openerp import SUPERUSER_ID


class accept_referral_wizard(osv.TransientModel):

    _name = 'nh.etake_list.accept_referral_wizard'
    _columns = {
        'tci_location_id': fields.many2one('nh.clinical.location', 'Location To Come In', domain=[['context_ids.name', 'in', ['etakelist']]]),
        'referral_activity_id': fields.many2one('nh.activity', 'Referral Activity')
    }

    def submit(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)
        activity_pool = self.pool['nh.activity']

        activity_pool.submit(cr, SUPERUSER_ID, data.referral_activity_id.id, {
            'location_id': data.tci_location_id.id, 'tci_location_id': data.tci_location_id.id}, context=context)
        activity_pool.complete(cr, uid, data.referral_activity_id.id, context=context)

        return {'type': 'ir.actions.act_window_close'}