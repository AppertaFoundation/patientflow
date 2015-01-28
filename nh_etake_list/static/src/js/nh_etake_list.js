/**
 * Created by colin on 27/01/15.
 */

openerp.nh_etake_list = function(instance){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    var kiosk_mode = false;

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
            } else {
                $sub_menu = this.$secondary_menus.find('.oe_secondary_menu[data-menu-parent=' + $clicked_menu.attr('data-menu') + ']');
                $main_menu = $clicked_menu;
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
            this.$secondary_menus.find('.active').removeClass('active');

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

            var activeMenu = $('.oe_secondary_menu').not(':hidden');
            var sectionTitles = activeMenu.find('.oe_secondary_menu_section');
            var sectionLists = activeMenu.find('.oe_secondary_submenu');
            var navbarDiv = $('<div class="navbar"></div>');
            var userMenu = $('.oe_user_menu_placeholder');
            if(activeMenu.find('.navbar').length < 1){
                activeMenu.prepend(navbarDiv);
            }else{
                activeMenu.find('.navbar').remove();
                activeMenu.prepend(navbarDiv);
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
                    sectionTitles.each(function(index) { $(this).removeClass('active'); });
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
            });


            // move the menu placeholder into nav if don't need top menu
            if($('.oe_application_menu_placeholder .active').css('display') == 'none'){
                userMenu.appendTo(navbarDiv);
                $('#oe_main_menu_navbar').hide();
            }
        }
    });





}