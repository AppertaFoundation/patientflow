/**
 * Created by colin on 27/01/15.
 */

openerp.nh_etake_list_theme = function(instance){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var kiosk_mode = false;
    var initKanban = false;

    instance.web.Menu.include({
        open_menu: function(id){
            this.current_menu = id;
            this.session.active_id = id;
            var $clicked_menu, $sub_menu, $main_menu;
            $clicked_menu = this.$el.add(this.$secondary_menus).find('a[data-menu=' + id + ']');
            this.trigger('open_menu', id, $clicked_menu);

            if (this.$secondary_menus.has($clicked_menu).length) {
                $sub_menu = $clicked_menu.parents('.oe_secondary_menu');
                $main_menu = this.$el.find('a[data-menu=' + $sub_menu.data('menu-parent') + ']');
                $('.oe_secondary_menu_section').removeClass('active');
                if(typeof($sub_menu.children('ul').attr('data-tab-id')) !== 'undefined'){
                    $('.oe_secondary_menu_section[data-tab-id='+$sub_menu.children('ul').attr('data-tab-id')+']').addClass('active');
                }
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
                $('.oe_secondary_menu_section').removeClass('active');
                $('.oe_secondary_menu_section[data-tab-id='+$sub_menu.attr('data-tab-id')+']').addClass('active');
            }



            // Activate current main menu
            this.$el.find('.active').removeClass('active');
            $main_menu.parent().addClass('active');


            // Show current sub menu
            this.$secondary_menus.find('.oe_secondary_menu').hide();
            $sub_menu.show();

            // Hide/Show the leftbar menu depending of the presence of sub-items
            if (! kiosk_mode){
                this.$secondary_menus.parent('.oe_leftbar').toggle(!!$sub_menu.children().length);
            }

            // Activate current menu item and show parents
            if($clicked_menu.parents('.oe_user_menu_placeholder').length < 1){
                this.$secondary_menus.find('.active').not('.oe_secondary_menu_section').removeClass('active');
            }


            if ($main_menu !== $clicked_menu) {
                if (! kiosk_mode){
                    $clicked_menu.parents().show();
                }
                if ($clicked_menu.is('.oe_menu_toggler')) {
                    $clicked_menu.toggleClass('oe_menu_opened').siblings('.oe_secondary_submenu:first').toggle();
                } else {
                    $clicked_menu.parent().addClass('active');
                }
            }
            // add a tooltip to cropped menu items
            this.$secondary_menus.find('.oe_secondary_submenu li a span').each(function() {
                $(this).tooltip(this.scrollWidth > this.clientWidth ? {title: $(this).text().trim(), placement: 'right'} :'destroy');
            });

            //var activeMenu = $('.oe_secondary_menu').not(':hidden');
            var sectionTitles = $sub_menu.find('.oe_secondary_menu_section');
            var sectionLists = $sub_menu.find('.oe_secondary_submenu');
            var navbarDiv = $('<div class="navbar"></div>');
            var userMenu = $('.oe_user_menu_placeholder');
            if($main_menu.parent().css('display') == "none"){
                if($('.oe_secondary_menu .oe_user_menu_placeholder').length < 1){
                    userMenu.clone(true).appendTo(navbarDiv);
                }
               $('#oe_main_menu_navbar').hide();
                if($("#oe_main_menu_navbar").css('display') == "none"){
                    $(".openerp.openerp_webclient_container").css('height', '100%');
                }
            }
            if($sub_menu.find('.navbar').length < 1){
                $sub_menu.prepend(navbarDiv);
            }else{
                $sub_menu.find('.navbar').remove();
                $sub_menu.prepend(navbarDiv);

            }
            sectionTitles.each(function(index){
                // set the tab id on the section header
                $(this).attr('data-tab-id', index);

                // set the tab id on the list itself
                $(this).next('ul').attr('data-tab-id', index);

                // show / hide the list based on if it is currently 'active' or not

                if($(this).next('ul').children('.active').length > 0){
                    $(this).addClass('active');
                    $(this).next('ul').show();
                }else{
                    $(this).next('ul').hide();
                }

                userMenu.show();

                // set up events to 'switch tabs'
                $(this).on('click', function(){
                    var tabId = $(this).attr('data-tab-id');
                    $(this).addClass('active');
                    sectionLists.each(function(index){
                        if($(this).attr('data-tab-id') == tabId){
                            $(this).show();
                        }else{
                            $(this).hide();
                        }
                    });
                });

                navbarDiv.append($(this));
                console.log(userMenu.length);
                if(navbarDiv.find('.oe_user_menu_placeholder').length < 1){
                    userMenu = $('.oe_user_menu_placeholder').first();
                    userMenu.clone(true).appendTo(navbarDiv);
                }
            });
        }
    });

    instance.web.FormView.include({
        can_be_discarded: function() {
            if (this.$el.is('.oe_form_dirty')) {
                  var popup_content = '<div><p>The record has been modified, your changes will be discarded.</p><p>Please save or discard your changes.</p></div>';
                  var popup = new instance.web.Dialog(this, {
                      title: _t('Warning'),
                      size: 'medium',
                      buttons: {
                          Ok: function() {
                              this.parents('.modal').modal('hide');
                          }}
                  }, $(popup_content));
                  popup.open();
                  return false;

                this.$el.removeClass('oe_form_dirty');
            }
        },
        on_button_cancel: function(event){
            var self = this;
            if (this.get('actual_mode') === 'create') {
                        this.trigger('history_back');
            } else {
                this.to_view_mode();
                $.when.apply(null, this.render_value_defs).then(function(){
                    self.trigger('load_record', self.datarecord);
                });
            }
            this.trigger('on_button_cancel');
            return false;
        }
    });

    instance.web_kanban.KanbanView.include({
        do_show: function() {
            $('.oe_view_manager_switch').hide();
            if (this.$buttons) {
                this.$buttons.show();
            }
            this.do_push_state({});
            return this._super();
        },
        do_hide: function(){
            $('.oe_view_manager_switch').show();
            if (this.$buttons) {
                this.$buttons.hide();
            }
            return this._super();
        },
        do_add_group: function() {
            var self = this;
            self.do_action({
                name: _t("Add column"),
                res_model: self.group_by_field.relation,
                views: [[false, 'form']],
                type: 'ir.actions.act_window',
                target: "new",
                context: self.dataset.get_context(),
                flags: {
                    action_buttons: false,
                }
            });



            var am = instance.webclient.action_manager;
            var form = am.dialog_widget.views.form.controller;
            form.on("on_button_cancel", am.dialog, am.dialog.close);
            form.on('record_created', self, function(r) {
                (new instance.web.DataSet(self, self.group_by_field.relation)).name_get([r]).done(function(new_record) {
                    am.dialog.close();
                    var domain = self.dataset.domain.slice(0);
                    domain.push([self.group_by, '=', new_record[0][0]]);
                    var dataset = new instance.web.DataSetSearch(self, self.dataset.model, self.dataset.get_context(), domain);
                    var datagroup = {
                        get: function(key) {
                            return this[key];
                        },
                        value: new_record[0],
                        length: 0,
                        aggregates: {},
                    };
                    var new_group = new instance.web_kanban.KanbanGroup(self, [], datagroup, dataset);
                    self.do_add_groups([new_group]).done(function() {
                        $(window).scrollTo(self.groups.slice(-1)[0].$el, { axis: 'x' });
                    });
                });
            });
        },
    });

}
