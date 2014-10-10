require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'views/rdm/concept-tree',
    'views/rdm/concept-report',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport) {
    $(document).ready(function() {
        var appHeader = $("#appheader"),
            sidebar = $("#sidebar"),
            topToHeaderPx = appHeader.offset().top,
            topToSidebarBottomPx = sidebar.offset().top + sidebar.height(),
            sidebarWidth = sidebar.outerWidth(),
            // Models and views
            concept = new ConceptModel({
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

        $(window).scroll(function() {
            var topToFooterPx = $(".footer").offset().top - $(window).scrollTop();

            if (window.scrollY >= topToHeaderPx) {
                appHeader.addClass("fixed");
                if (conceptReport.$el.height() > sidebar.height()) {
                    sidebar.addClass("fixed-menu");
                    sidebar.css("width", sidebarWidth);
                    if (topToFooterPx < topToSidebarBottomPx) {
                        sidebar.css("margin-top", topToFooterPx - topToSidebarBottomPx);
                    } else {
                        sidebar.css("margin-top", "10px");
                    }
                }
            } else {
                appHeader.removeClass("fixed");
                sidebar.removeClass("fixed-menu");
                sidebar.css("margin-top", "0px");
                conceptReport.$el.removeClass("fixed-spacer");
                conceptReport.$el.css("margin-top", "0px");
            }
        });
    });
});