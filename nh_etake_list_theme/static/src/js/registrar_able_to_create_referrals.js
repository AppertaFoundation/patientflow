/**
 * Created by neova on 12/05/15.
 */
(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'registrar_able_to_create_referrals',
        name: _t("Reconcile the demo bank statement"),
        path: '/web?debug=',
        //mode: 'test',

        // TODO : identify menu by data-menu attr or text node ?
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
            }

        ]
    });

}());