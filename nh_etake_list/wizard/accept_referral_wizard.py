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
        view_pool = self.pool['ir.ui.view']

        activity_pool.submit(cr, SUPERUSER_ID, data.referral_activity_id.id, {
            'location_id': data.tci_location_id.id, 'tci_location_id': data.tci_location_id.id}, context=context)
        activity_pool.complete(cr, uid, data.referral_activity_id.id, context=context)

        view_id = view_pool.search(cr, SUPERUSER_ID, [['name', '=', 'NH eTake List Overview Kanban View']], context=context)

        view = {
            'type': 'ir.actions.act_window',
            'res_model': 'nh.etake_list.overview',
            'name': 'Referral Board',
            'view_type': 'form',
            'view_mode': 'kanban',
            'context': {'search_default_group_by_state': 1},
            'domain': [('state', 'not in', ['Done', 'Other', 'dna', 'to_dna', 'admitted']),
                       ('hours_from_discharge', '<', 12)],
            'view_id': view_id[0],
            'target': 'current',
            'clear_breadcrumb': True
        }

        return view