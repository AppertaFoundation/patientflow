from openerp.osv import osv, fields
from openerp import SUPERUSER_ID


class print_paper_take_list_wizard(osv.TransientModel):

    _name = 'nh.etake_list.print_paper_take_list_wizard'
    _sorting_options = [
        ['H', '14 Hour Target'],
        ['W', 'Ward']
    ]
    _columns = {
        'sort_by': fields.selection(_sorting_options, 'Sort list by'),
    }

    def print_report(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)
        # activity_pool = self.pool['nh.activity']
        #
        # activity_pool.submit(cr, SUPERUSER_ID, data.referral_activity_id.id, {
        #     'location_id': data.tci_location_id.id, 'tci_location_id': data.tci_location_id.id}, context=context)
        # activity_pool.complete(cr, uid, data.referral_activity_id.id, context=context)
        report_info = self.pool['report'].get_action(cr, uid, [], 'nh_etake_list.takelist_report_view', data=data.sort_by, context=context)
        return {
            'type': 'ir.actions.act_close_wizard_and_print_report',
            'tag': report_info
        }

    # def _print_report(self, cr, uid, ids, data, context=None):
    #     if context is None:
    #         context = {}
    #     data = self.pre_print_report(cr, uid, ids, data, context=context)
    #     data['form'].update(self.read(cr, uid, ids, ['initial_balance', 'filter', 'page_split', 'amount_currency'])[0])
    #     if data['form'].get('page_split') is True:
    #         return self.pool['report'].get_action(cr, uid, [], 'account.report_partnerledgerother', data=data, context=context)
    #     return self.pool['report'].get_action(cr, uid, [], 'account.report_partnerledger', data=data, context=context)
