/**
 * Created by colin on 27/01/15.
 */

$(document).ready(function(){

    var activeMenu = $('.oe_secondary_menu').not(':hidden');
    var sectionTitles = activeMenu.find('.oe_secondary_menu_section');
    var sectionLists = activeMenu.find('.oe_secondary_submenu');
    var navbarDiv = $('<div class="navbar"></div>');
    activeMenu.prepend(navbarDiv);
    sectionTitles.each(function(index){
        // set the tab id on the section header
        $(this).attr('data-tab-id', index);

        // set the tab id on the list itself
        $(this).next('ul').attr('data-tab-id', index);

        // show / hide the list based on if it is currently 'active' or not

        if($(this).next('ul').children('.active').length > 0){
            $(this).next('ul').show();
        }else{
            $(this).next('ul').hide();
        }

        // set up events to 'switch tabs'
        $(this).on('click', function(){
            var tabId = $(this).attr('data-tab-id');
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
});