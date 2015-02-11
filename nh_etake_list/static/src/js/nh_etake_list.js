openerp.nh_etake_list = function (instance) {

    instance.web.ListView.include({
        init: function(parent, dataset, view_id, options) {
            if (options.action){
                if (['Rejected Referrals','Patient Referral Forms','Referrals','Arrivals','To be Clerked','Clerkings in Progress','Senior Reviews','Consultant Reviews','To be Discharged','Recently Admitted Patients'].indexOf(options.action.name) > -1){
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
    });

    instance.web.Model.include({
        call_button: function (method, args) {
            instance.web.pyeval.ensure_evaluated(args, {});
            if (window.location.hash.indexOf("view_type=kanban") > -1 && this.name == 'nh.etake_list.overview' && method != 'start_clerking'){
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

}