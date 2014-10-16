require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'views/rdm/concept-tree',
    'views/rdm/concept-report',
    'views/concept-search',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport, ConceptSearch) {
    $(document).ready(function() {
        var appHeader = $("#appheader");
        var sidebar = $("#sidebar");
        var topToHeaderPx = appHeader.offset().top;
        var topToSidebarBottomPx = sidebar.offset().top + sidebar.height();
        var sidebarWidth = sidebar.outerWidth();
            // Models and views
        var concept = new ConceptModel({
            id: $('#selected-conceptid').val()
        });
        var conceptTree = new ConceptTree({
            el: $('#jqtree')[0],
            model: concept
        });
        var conceptReport = new ConceptReport({
            el: $('#concept_report')[0],
            model: concept
        });
        var conceptsearch = new ConceptSearch({ 
            el: $('#rdm-concept-search-container')[0],
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
                    conceptReport.$el.css("margin-top", "95px");
                    if (topToFooterPx < topToSidebarBottomPx) {
                        sidebar.css("margin-top", topToFooterPx - topToSidebarBottomPx);
                    } else {
                        sidebar.css("margin-top", "10px");
                    }
                } else {
                    sidebar.css("margin-top", "90px");
                    conceptReport.$el.css("margin-top", "90px");
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