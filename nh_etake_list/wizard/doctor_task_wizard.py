from openerp.osv import osv, fields


class doctor_task_wizard(osv.TransientModel):

    _name = 'nh.clinical.doctor_task_wizard'
    _columns = {
        'name': fields.char('Task Name', size=300, required=True),
        'blocking': fields.boolean('Blocking'),
        'patient_id': fields.many2one('nh.clinical.patient', 'Patient'),
        'spell_id': fields.many2one('nh.activity', 'Spell')
    }

    def submit(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context)

        doctor_task_pool = self.pool['nh.clinical.doctor.task']
        activity_pool = self.pool['nh.activity']

        activity_id = doctor_task_pool.create_activity(cr, uid, {
            'summary': data.name,
            'parent_id': data.spell_id.id,
            'patient_id': data.patient_id.id
        }, {'blocking': data.blocking}, context=context)

        activity_pool.submit(cr, uid, activity_id, {}, context=context)

        return {'type': 'ir.actions.act_window_close'}