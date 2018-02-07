require([
    'jquery',
    'arches',
    "bootstrap", 
    "moment", 
    "bootstrap-datetimepicker"
], function($, arches) {
    $(document).ready(function() {
        //Scrolling, Get initial offsets for the app header
        var header_offset = $("#appheader").offset();
        
        //Determine the trigger to start scrolling the sidebar.  Sidebar should scroll when the position of the bottom of the CRUD form 
        //coincides with the bottom of the sidebar.  Determine which div is lower, then set the trigger to that div
        var sidebar = $("#sidebar");
        var crud = $("#crud");
        var sidebar_bottom = sidebar.offset().top + sidebar.height();
        
        //There seems to be a bug in jQuery.  When setting the position class during scrolling the menu width gets reset.
        //Fix this by getting initial width of menu.  Use to reset the menu width on scroll
        var menu_width = $("#sidebar").width();
        
        $(function () {
            $('.datetimepicker').datetimepicker({pickTime: false});
        });
        
        //Manage position/scrolling of App header, menu, and CRUD forms based on user scrolling
        $( window ).scroll(function() {
            
            //Check to see if user has scrolled window enough to fix position of App header
            if(window.scrollY >= header_offset.top) { 
  
                //Fix App header to top of window
                $(".sticky").addClass("fixed");

                        //This next bit scrolls the sidebar menu.  We only need to worry about this if the crud form height is greater than the sidebar height
                        var sidebar_height = sidebar.height();
                        var crud_height = crud.height();

                        if (crud_height > sidebar_height) {

                                //Set top of menu (make it sticky)
                                $("#sidebar").addClass("fixed-menu");
                                $("#sidebar").css("width", menu_width);
                                
                                //give the crud div a spacer so that it doesn't appear to jump on initial scroll
                                $("#crud").css("margin-top", "80px");
                                $("#sidebar").css("margin-top", "20px");

                                //Now scroll the sidebar if the footer threatens to bump into it.  
                                var footer_top = $(".footer").offset().top - $(window).scrollTop();

                                if(footer_top < sidebar_bottom) { 
                                        
                                        //allow sidebar to scroll
                                        $("#sidebar").css("margin-top", footer_top - sidebar_bottom + 0);

                                    } else { 

                                        //user is scrolling up and we need to re-set the top of the sidebar
                                        $("#sidebar").css("margin-top", "0px");

                                }

                            } else {

                            //add spacers so that crud and sidebar forms don't appear to jump
                            $("#sidebar").css("margin-top", "90px");
                            $("#crud").css("margin-top", "90px");

                        }


            //User has now scrolled the entire window back up beyond the App header.  Unstick the App header 
            //and put the sidebar and crud forms back into their original places
            } else {

                //Un stick App header, menu, CRUD when user scrolls up to top of window
                $(".sticky").removeClass("fixed");
                $("#sidebar").removeClass("fixed-menu");
                $("#sidebar").css("margin-top", "0px");

                $("#crud").removeClass("fixed-spacer");
                $("#crud").css("margin-top", "0px");

            }

        });

        var dirty = false;
        
        require(['views/forms/' + $('#form-id').val()], function (FormView) {
            if (FormView) {
                var formView = new FormView({
                    el: $('#resource_data_management_form')[0]
                });
                formView.on('change', function () {
                    dirty = true;
                });
            }
        });

        var formurl = '';
        var navigateForm = function () {
            $('#nav-confirm-modal').modal('hide');
            $('.form-load-mask').show();
            document.location.href = formurl;
        }

        $('.form-link').click(function (e) {
            formurl = $(e.target).data().formurl;
            if (dirty) {
                $('#nav-confirm-modal').modal('show');
            } else {
                navigateForm();
            }
        });

        $('.nav-confirm-btn').click(function () {
            navigateForm();
        });

        $('#crud_menu').on("change", function(e) {
            if (dirty) {
                // make sure they are cool with losing edits before switching...
            } else {
                $(this).select2("val", $('option:selected', this).text())
                document.location.href = $('option:selected', this).attr('data-formurl');
            }
        });

    });
});
