/**
 * Created by neova on 12/05/15.
 */
(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'junior_doctor_able_to_update_patient_arrival',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',


        steps: [

            {
                title:     _t("Login page Loaded"),
                element:   '.oe_topbar_name'
            },

            {
                title:     _t("Referral Board Loaded"),
                element:   '.oe_menu_text:contains("Referral Board")'
            },

            {
                title:     _t("Notify patient arrival (click on'Arrived'  button)"),
                element:   'td.oe_kanban_column:nth-child(2) .oe_fold_column.oe_kanban_record:first() button'
            },
            {
                title:     _t("patient arrival updated and patient is in To be clerked stage"),
                waitFor:   ('td.oe_kanban_column:nth-child(3) div.oe_fold_column.oe_kanban_record').length + 1
            }
        ]
    });

}());