require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'views/rdm/concept-tree',
    'views/rdm/concept-report',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport) {
    jQuery(document).ready(function() {
        var header_offset = $("#appheader").offset(),
            sidebar = $("#sidebar"),
            crud = $("#crud"),
            sidebar_bottom = sidebar.offset().top + sidebar.height(),
            menu_width = $("#sidebar").outerWidth();


        $(window).scroll(function() {
            var sidebar_height = sidebar.height(),
                crud_height = crud.height(),
                footer_top = $(".footer").offset().top - $(window).scrollTop();

            if (window.scrollY >= header_offset.top) {
                $(".sticky").addClass("fixed");
                
                if (crud_height > sidebar_height) {
                    $("#sidebar").addClass("fixed-menu");
                    $("#sidebar").css("width", menu_width);
                    
                    if (footer_top < sidebar_bottom) {
                        $("#sidebar").css("margin-top", footer_top - sidebar_bottom);
                    } else {
                        $("#sidebar").css("margin-top", "10px");
                    }
                }

            } else {
                $(".sticky").removeClass("fixed");
                $("#sidebar").removeClass("fixed-menu");
                $("#sidebar").css("margin-top", "0px");
                $("#crud").removeClass("fixed-spacer");
                $("#crud").css("margin-top", "0px");
            }

        });
    });



    $(document).ready(function() {
        var concept = new ConceptModel({
                id: $('#selected-conceptid').val()
            }),
            conceptTree = new ConceptTree({
                el: $('#jqtree')[0],
                model: concept
            }),
            conceptReport = new ConceptReport({
                el: $('#concept_report')[0],
                model: concept
            });

        concept.on('change', function() {
            window.history.pushState({}, "conceptid", concept.get('id'));
        });

        conceptTree.on('conceptMoved', function() {
            conceptReport.render();
        });

        conceptReport.on({
            'valueSaved': function() {
                conceptTree.render();
            },
            'conceptDeleted': function() {
                conceptTree.render();
            },
            'conceptAdded': function() {
                conceptTree.render();
            }
        });
    });
});