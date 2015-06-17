from openerp.osv import osv, fields
from openerp import SUPERUSER_ID


class print_paper_take_list_wizard(osv.TransientModel):

    _name = 'nh.etake_list.print_paper_take_list_wizard'
    _sorting_options = [
        ['P', 'PTWR'],
        ['J', 'Junior Activity'],
        ['H', '14 Hour Target'],
        ['W', 'Location']
    ]
    _columns = {
        'sort_by': fields.selection(_sorting_options, 'Sort list by'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)
        if not context:
            context = {}
        context['landscape'] = True
        report_info = self.pool['report'].get_action(cr, uid, [], 'nh_etake_list.takelist_report_view', data=data.sort_by, context=context)
        return {
            'type': 'ir.actions.act_close_wizard_and_print_report',
            'tag': report_info
        }

