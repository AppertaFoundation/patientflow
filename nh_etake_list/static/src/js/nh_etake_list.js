openerp.nh_etake_list = function (instance) {

    instance.web.ListView.include({
        init: function(parent, dataset, view_id, options) {
            if (options.action){
                if (['Patient Referral Forms','Referrals','Arrivals','To be Clerked','Clerkings in Process','Senior Reviews','Consultant Reviews','To be Discharged','Recently Admitted Patients'].indexOf(options.action.name) > -1){
                    options.selectable = false;
                };
            }
            this._super.apply(this, [parent, dataset, view_id, options]);
        },
    });

}