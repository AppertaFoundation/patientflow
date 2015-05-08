(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'referral_nurse_able_to_update_patient_arrival',
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
                title:     _t("Referral Board"),
                element:   '.oe_menu_text:contains("Referral Forms")'
            },

             {
                title:     _t("Update patient arrival"),
                element:   'td.oe_kanban_column:nth-child(2) .oe_fold_column.oe_kanban_record:first() button'
            },

        ]
    });

}());
