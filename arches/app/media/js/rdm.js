require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'views/rdm/concept-tree',
    'views/rdm/concept-report',
    'views/concept-search',
        'views/rdm/modals/add-scheme-form',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport, ConceptSearch, AddSchemeForm) {
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

        concept.on({
            'change': function(){
                window.history.pushState({}, "conceptid", concept.get('id'));
            },
            'save': function(){
                conceptTree.render();
                conceptReport.render();
                conceptid = concept.get('id');
                concept.clear();
                concept.set('id', conceptid);
            },
            'delete': function(){
                conceptTree.render();
                conceptReport.render();
                conceptid = concept.get('id');
                concept.clear();
                concept.set('id', conceptid);
            }
        });

        conceptTree.on({
            'conceptMoved': function() {
                conceptReport.render();
            },
            'conceptSelected': function(conceptid){
                concept.clear();
                concept.set('id', conceptid);
                conceptTree.render();
                conceptReport.render();
            }
        });

        conceptReport.on({
            'conceptSelected': function(conceptid) {
                concept.clear();
                concept.set('id', conceptid);
                conceptTree.render();
                conceptReport.render();
            },
            'parentsChanged': function() {
                conceptTree.render();
                conceptReport.render();
            }//,
            // 'conceptAdded': function() {
            //     conceptTree.render();
            // }
        });

        conceptsearch.on("select2-selecting", function(e, el) {
            concept.clear();
            concept.set('id', e.val);
            conceptTree.render();
            conceptReport.render();
        }, conceptsearch);

        $('a[data-toggle="#add-scheme-form"]').on( "click", function(){
            var self = this;
            var form = new AddSchemeForm({
                el: $('#add-child-form')[0]
            });
            form.modal.modal('show');
            form.on({
                'conceptSchemeAdded': function(){
                    conceptTree.render();
                    conceptReport.render();
                }
            })
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