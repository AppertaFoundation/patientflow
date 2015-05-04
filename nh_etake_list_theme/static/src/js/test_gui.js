(function () {
    'use strict';

    var _t = openerp._t;


    openerp.Tour.register({
        id: 'refferal_nurse_able_to_create_referral',
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
                title:     _t("Save"),
                element:   '.oe_form_button_save'
            }

           /* {
                title:      _t("Insert Data into referral form"),
                element:    '#oe-field-input-103'
            }
*/

/*
           // Overriding template
              {

                title:     _t("Click on Inbox"),
                element:   '.oe_menu_text:contains("Inbox")',
                placement: 'bottom',
                content:   _t("<li>Inbox gives yoau access to all message related to tickets</li><li>These are also shown in detailed ticket view</li>"),
                popover:   {  next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },

            {
                waitNot:   '.popover.tour',
                title:     _t("Click on Tickets"),
                element:   '.oe_secondary_menus_container span.oe_menu_text:contains("Tickets")',
                placement: 'right',
                content:   _t("Here You are able to raise(create) tickets and review their status"),
                popover:   { next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },

            {

                title:     _t("Click on Create button"),
                element:   'button:contains("Create")',
                placement: 'bottom',
                content:   _t("To create a new ticket,<br> click on the create button"),
                popover:   { fixed: true },

            },


            {
                title:     _t("Issue Title"),
                element:   '#oe-field-input-3',
                placement: 'bottom',
                content:   _t("This is mandatory field"),
                popover:   { next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },


            {
                waitNot:   '.popover.tour',
                title:     _t("Description"),
                element:   'textarea[name=description]',
                placement: 'left',
                content:   _t("Please enter description including scope and impact"),
                popover:   { next: _t("Next")},
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },


             {
                waitNot:   '.popover.tour',
                title:     _t("Click on Save"),
                element:   '.oe_button.oe_form_button_save.oe_highlight:button:contains("Save")',
                placement: 'bottom',
                content:   _t("Click on Save button to save the ticket"),
                popover:   { next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
             },

             {
                waitNot:   '.popover.tour',
                title:     _t("Click on Tickets"),
                element:   '.oe_secondary_menus_container span.oe_menu_text:contains("Tickets")',
                placement: 'bottom',
                content:   _t("Here You are able to raise(create) tickets and review their status"),
                popover:   { fixed: true },
             },

             {
                waitFor:   'button:contains("Create"):visible',
                title:     _t("Kanban View"),
                element:   '.oe_vm_switch_kanban',
                placement: 'bottom',
                content:   _t("<li>Every ticket in kanaban view is represnted by an index card</li><li>Click on any ticket for detailed view</li>"),
                popover:   { next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },

            {
                title:     _t("Service Level"),
                element:   'label:contains("Service Level")',
                placement: 'Right',
                content:   _t("Initially Empty, <b>Service Level</b> will be assigned by NH team,<br>SLA deadline will be calculated accordingly"),
                popover:   { next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },

            {
                //waitFor:   '.popover.tour',
                //waitFor:    '.oe_compose_post',
                //waitFor:   '.oe_dropdown_toggle.oe_dropdown_arrow:contains("More")',
                title:     _t("Followers"),
                element:   '#ui-id-7',
                placement: 'bottom',
                content:   _t("<b>Followers</b> of a ticket will receive notification of all stage updates and messages"),
                popover:   { next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },

            {
                //waitFor:   'button:contains("Create"):visible',
                title:     _t("Send message"),
                element:   '.oe_compose_post',
                placement: 'bottom',
                content:   _t("By clicking on <b>Send a Message</b> you can add a comment or attach screenshot"),
                popover:   { next: _t("Next") },
                template: _t('<div class="popover tour fixed">  <div class="arrow"></div> <h3 class="popover-title"></h3> <div class="popover-content"></div> <nav class="popover-navigation"> <button class="btn btn-sm btn-default" data-role="next">Next</button> </div>'),
            },


            {
                //waitFor:   'button:contains("Create"):visible',
                title:     _t("Stages in detail"),
                element:   '.label:Contains("Input Queue")',
                placement: 'bottom',
                content:   _t("<li>When ticket is in any stages between <b>Input Queue</b> to <b>Release</b>, means ticket is worked on and progress according to the agile kanban method</li><li> <b>Done</b>: Request has benn fullfilled</li><li><b>Cancelled</b>: Request has been cancelled because it is a duplicate or invalid</li> "),
                popover:   { next: _t("Next") },

            },
//
//            {
//                title: 'Press the project button ami',
//                element: '.oe_menu_toggler .oe_menu_text:contains("Project")',
//            },
//
//            {
//                title: 'Press the purchase button',
//                element: '.oe_menu_toggler .oe_menu_text:contains("Purchase")',
//            },


/*
            {
                //waitFor:   'button:contains("Create"):visible',
                //waitFor:   '.popover.tour',
                title:     _t("Click on More"),
                element:   '.label:Contains("More")',
                placement: 'bottom',
                content:   _t("<li> <b>Done</b>: Request has benn fullfilled</li><br><li><b>Cancelled</b>: Request has been cancelled because it is a duplicate or invalid</li> "),
                popover:   { fixed: true },
            }
*/


/*

            {
                waitNot:   '.popover.tour',
                element:   'button[data-action=edit]',
                placement: 'bottom',
                title:     _t("Edit this page - Shreyans"),
                content:   _t("Every page of your website can be modified through the <i>Edit</i> button."),
                popover:   { fixed: true },
            },
            {
                element:   'button[data-action=snippet]',
                placement: 'bottom',
                title:     _t("Insert building blocks"),
                content:   _t("Click here to insert blocks of content in the page."),
                popover:   { fixed: true },
            },
            {
                snippet:   '#snippet_structure .oe_snippet:first',
                placement: 'bottom',
                title:     _t("Drag & Drop a Banner"),
                content:   _t("Drag the Banner block and drop it in your page."),
                popover:   { fixed: true },
            },
            {
                waitFor:   '.oe_overlay_options .oe_options:visible',
                element:   '#wrap .carousel:first div.carousel-content',
                placement: 'top',
                title:     _t("Customize banner's text"),
                content:   _t("Click in the text and start editing it."),
                sampleText: 'Here, a customized text',
            },
            {
                waitNot:   '#wrap .carousel:first div.carousel-content:has(h2:'+
                    'containsExact('+_t('Your Banner Title')+')):has(h3:'+
                    'containsExact('+_t('Click to customize this text')+'))',
                element:   '.oe_snippet_parent:visible',
                placement: 'bottom',
                title:     _t("Get banner properties"),
                content:   _t("Select the parent container to get the global options of the banner."),
                popover:   { fixed: true },
            },

            {
               // waitNot:   '.popover.tour',
                element:   '.oe_application_menu_placeholder .oe_menu_text:contains("Project"):visible',
                placement: 'bottom',
                title:     _t("Click on Project"),
                content:   _t("Click on <b>Project</b> and go to issue"),
                popover:   {  next: _t("Start Tutorial"), end: _t("Skip It") },
            },

            {
                waitNot:   '.popover.tour',
                element:   '.oe_secondary_submenu li.active span.oe_menu_text:contains("Issues")',
                placement: 'bottom',
                title:     _t("Click on Issues"),
                content:   _t("Click on <b>Project</b> and go to issue"),
                popover:   {  next: _t("Start Tutorial"), end: _t("Skip It") },
            },


*/



        ]
    });

}());
