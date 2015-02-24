__author__ = 'colin'
from openerp import api, models
from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as dtf

class ParticularReport(models.AbstractModel):
    _name = 'report.nh_etake_list.takelist_report'
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('nh_etake_list.takelist_report_view')
        overview_pool = self.pool['nh.etake_list.overview']
        clerking_take_list_ids = overview_pool.search(self._cr, self._uid, [['state', 'not in', ['discharged', 'done']], ['clerking_started', '!=', False]], order='clerking_started desc, id asc')
        non_clerking_take_list_ids = overview_pool.search(self._cr, self._uid, [['state', 'not in', ['discharged', 'done']], ['clerking_started', '=', False]], order='id asc')
        take_list = overview_pool.read(self._cr, self._uid, clerking_take_list_ids + non_clerking_take_list_ids)
        for patient in take_list:
            if patient['dob']:
                dob_delta = datetime.strptime(patient['dob'], dtf)
                patient['dob'] = datetime.strftime(dob_delta, '%d/%m/%Y')
            if patient['clerking_started']:
                clerking_start = datetime.strptime(patient['clerking_started'], dtf)
                clerking_deadline = clerking_start + timedelta(hours=14)
                patient['clerking_deadline'] = datetime.strftime(clerking_deadline, dtf)
        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
            'take_list': take_list,
            }
        return report_obj.render('nh_etake_list.takelist_report_view', docargs)
