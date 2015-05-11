/**
 * Created by neova on 11/05/15.
 */
(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'referral_nurse_ able_to_update_patient_arrival',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',


        steps: [

            {
                title:     _t("Login page"),
                element:   '.oe_topbar_name'
            },

            {
                title:     _t("Referral form"),
                element:   '.oe_menu_text:contains("Referral Forms")'
            },

             {
                title:     _t("Create Referral"),
                element:   '.oe_button.oe_list_add.oe_highlight:contains("Create")'
            },

            {
                title:     _t("Select Patient"),
                element:   '#oe-field-input-16',
                sampleText: 'Klocko, Lindell'
            },
            {
                title:     _t("Enter Symptoms"),
                element:   'textarea[name=symptoms_notes]',
                sampleText: 'Test Symptom Notes'
            },
            {
                title:     _t("Enter Medical History"),
                element:   'textarea[name=medical_history_notes]',
                sampleText: 'Test Medical History Notes'
            },
            {
                title:     _t("Enter Allergies"),
                element:   'textarea[name=allergies]',
                sampleText: 'Test Allergies'
            },
            {
                title:     _t("Save"),
                element:   '.oe_form_button_save'
            },

            {
                title:     _t("Referral Created"),
                waitFor:   ('td.oe_kanban_column:nth-child(1) div.oe_fold_column.oe_kanban_record').length + 1
            }

        ]
    });

}());