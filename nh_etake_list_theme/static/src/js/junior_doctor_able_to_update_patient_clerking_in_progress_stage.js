(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'junior_doctor_able_to_update_patient_clerking_in_progress_stage',
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
                title:     _t("Clerk patient(click on 'Clerk'  button)"),
                element:   'td.oe_kanban_column:nth-child(3) .oe_fold_column.oe_kanban_record:first() button'
            },
            {
                title:     _t("Save"),
                element:   '.oe_form_button_save'
            },
            {
                title:     _t("patient stage updated to 'clerking in progress stage' "),
                waitFor:   ('td.oe_kanban_column:nth-child(4) div.oe_fold_column.oe_kanban_record').length + 1
            }
        ]
    });

}());