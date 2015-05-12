/**
 * Created by neova on 12/05/15.
 */
(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'junior_doctor_able_to_create_diagnosis_plans_tasks',
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
                title:     _t("Enter Diagnosis"),
                element:   'textarea[name=diagnosis]',
                sampleText: 'Test diagnosis'
            },
            {
                title:     _t("Enter Plan"),
                element:   'textarea[name=plan]',
                sampleText: 'Test plan'
            },
            {
                title:     _t("Create Task"),
                element:   '.oe_button.oe_form_button:contains("Create Task")'
            },
            {
                title:     _t("Enter Task"),
                element:   '.oe_form_field.oe_form_field_char.oe_form_required',
                sampleText: 'Test Tasks Name'
            },
/*
            {
                title:     _t("Blocking Tasks"),
                element:   '#oe-field-input-32:checked'
            },*/
            {
                title:     _t("Submit Tasks"),
                element:   '.oe_button.oe_form_button.oe_highlight'
            },
            {
                title:     _t("Save"),
                element:   '.oe_form_button_save'
            },
            {
                title:     _t("patient stage updated to 'clerking in progress stage' "),
                waitFor:   'td.oe_kanban_column:nth-child(4) div.oe_fold_column.oe_kanban_record'.length + 1
            }
        ]
    });

}());