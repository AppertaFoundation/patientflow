openerp.nh_etake_list = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;

    instance.web.ListView.include({
        init: function(parent, dataset, view_id, options) {
            if (options.action){
                if (['Rejected Referrals','Patient Referral Forms','Referrals','Arrivals','To be Clerked','Clerkings in Progress','Senior Reviews','Consultant Reviews','To be Discharged','Recently Admitted Patients','Discharged'].indexOf(options.action.name) > -1){
                    options.selectable = false;
                };
            }
            this._super.apply(this, [parent, dataset, view_id, options]);
        },
    });

    instance.web.FormView.include({
        init: function(parent, dataset, view_id, options) {
        	if (options.action != null && options.action.target != null && options.action.target == 'current_edit') {
        		options.initial_mode = "edit";
        	}

            this._super(parent, dataset, view_id, options);
        },
        load_form: function(data) {
            var self = this;
            if (!data) {
                throw new Error(_t("No data provided."));
            }
            if (this.arch) {
                throw "Form view does not support multiple calls to load_form";
            }
            this.fields_order = [];
            this.fields_view = data;

            this.rendering_engine.set_fields_registry(this.fields_registry);
            this.rendering_engine.set_tags_registry(this.tags_registry);
            this.rendering_engine.set_widgets_registry(this.widgets_registry);
            this.rendering_engine.set_fields_view(data);
            var $dest = this.$el.hasClass("oe_form_container") ? this.$el : this.$el.find('.oe_form_container');
            this.rendering_engine.render_to($dest);

            this.$el.on('mousedown.formBlur', function () {
                self.__clicked_inside = true;
            });

            this.$buttons = $(QWeb.render("FormView.buttons", {'widget':self}));
            if (this.options.$buttons) {
                this.$buttons.appendTo(this.options.$buttons);
            } else {
                this.$el.find('.oe_form_buttons').replaceWith(this.$buttons);
            }
            this.$buttons.on('click', '.oe_form_button_create',
                             this.guard_active(this.on_button_create));
            this.$buttons.on('click', '.oe_form_button_edit',
                             this.guard_active(this.on_button_edit));
            this.$buttons.on('click', '.oe_form_button_save',
                             this.guard_active(this.on_button_save));
            this.$buttons.on('click', '.oe_form_button_cancel',
                             this.guard_active(this.on_button_cancel));
            if (this.options.footer_to_buttons) {
                this.$el.find('footer').appendTo(this.$buttons);
            }

            this.$sidebar = this.options.$sidebar || this.$el.find('.oe_form_sidebar');
            if (!this.sidebar && this.options.$sidebar) {
                this.sidebar = new instance.web.Sidebar(this);
                this.sidebar.appendTo(this.$sidebar);
                if (this.fields_view.toolbar) {
                    this.sidebar.add_toolbar(this.fields_view.toolbar);
                }
                if (this.model != "nh.clinical.patient.referral.form"){
                    this.sidebar.add_items('other', _.compact([
                        self.is_action_enabled('delete') && { label: _t('Delete'), callback: self.on_button_delete },
                        self.is_action_enabled('create') && { label: _t('Duplicate'), callback: self.on_button_duplicate }
                    ]));
                }
                else{
                    this.sidebar.add_items('other', _.compact([
                        self.is_action_enabled('delete') && { label: _t('Delete'), callback: self.on_button_delete }
                    ]));
                }
            }

            this.has_been_loaded.resolve();

            // Add bounce effect on button 'Edit' when click on readonly page view.
            this.$el.find(".oe_form_group_row,.oe_form_field,label,h1,.oe_title,.oe_notebook_page, .oe_list_content").on('click', function (e) {
                if(self.get("actual_mode") == "view") {
                    var $button = self.options.$buttons.find(".oe_form_button_edit");
                    $button.openerpBounce();
                    e.stopPropagation();
                    instance.web.bus.trigger('click', e);
                }
            });
            //bounce effect on red button when click on statusbar.
            this.$el.find(".oe_form_field_status:not(.oe_form_status_clickable)").on('click', function (e) {
                if((self.get("actual_mode") == "view")) {
                    var $button = self.$el.find(".oe_highlight:not(.oe_form_invisible)").css({'float':'left','clear':'none'});
                    $button.openerpBounce();
                    e.stopPropagation();
                }
             });
            this.trigger('form_view_loaded', data);
            return $.when();
        },
    });

    instance.web.Model.include({
        call_button: function (method, args) {
            instance.web.pyeval.ensure_evaluated(args, {});
            if (instance.webclient.action_manager.inner_widget.active_view == 'kanban' && this.name == 'nh.etake_list.overview' && method != 'start_clerking'){
                return this.session().rpc('/web/dataset/call_button', {
                    model: this.name,
                    method: method,
                    // Should not be necessary anymore. Integrate remote in this?
                    domain_id: null,
                    context_id: args.length - 1,
                    args: args || []
                }).then(function(){
                    $('.oe_secondary_submenu .active .oe_menu_leaf').trigger('click');
                });
            }
            return this.session().rpc('/web/dataset/call_button', {
                model: this.name,
                method: method,
                // Should not be necessary anymore. Integrate remote in this?
                domain_id: null,
                context_id: args.length - 1,
                args: args || []
            });
        }
    });

    instance.web.ActionManager = instance.web.ActionManager.extend({
        ir_actions_act_close_wizard_and_print_report: function(action, options){
            if(!this.dialog){
                options.on_close();
            }
            this.dialog_stop();
            // trigger report print
            instance.webclient.action_manager.ir_actions_report_xml(action['tag'], action['tag']['data']);
            return $.when();
        }
    })

}
