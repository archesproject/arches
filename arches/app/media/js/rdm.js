require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'views/rdm/concept-tree',
    'views/rdm/concept-report',
    'views/concept-search',
    'views/rdm/modals/add-scheme-form',
    'views/rdm/modals/export-scheme-form',
    'views/rdm/modals/delete-scheme-form',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport, ConceptSearch, AddSchemeForm, ExportSchemeForm, DeleteSchemeForm) {
    $(document).ready(function() {
        var mode = 'scheme';
        if (window.location.search.search('mode=dropdown') === 1){
            mode = 'dropdown';
        }

        window.onpopstate = function(event) {
          //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
          //window.location = document.location;
        };

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
                //conceptTree.render();
                conceptReport.render();
                concept.reset()
            },
            'delete': function(){
                //conceptTree.render();
                conceptReport.render();
                concept.reset()
            }
        });

        conceptTree.on({
            'conceptMoved': function() {
                conceptReport.render();
            },
            'conceptSelected': function(conceptid){
                concept.clear();
                concept.set('id', conceptid);                   
                conceptReport.render();
            }
        });

        conceptReport.on({
            'conceptSelected': function(conceptid) {
                concept.clear();
                concept.set('id', conceptid);

                //conceptTree.render();
                conceptReport.render();
            },
            'parentsChanged': function() {
                //conceptTree.render();
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
                el: $('#add-scheme-form')
            });
            form.modal.modal('show');
            form.on({
                'conceptSchemeAdded': function(){
                    conceptTree.render();
                    conceptReport.render();
                }
            })
        });

        $('a[data-toggle="#export-scheme-form"]').on( "click", function(){
            var self = this;
            var form = new ExportSchemeForm({
                el: $('#export-scheme-form')
            });
            form.modal.modal('show');
        });

        $('a[data-toggle="#delete-scheme-form"]').on( "click", function(){
            var self = this;
            var form = new DeleteSchemeForm({
                el: $('#delete-scheme-form')
            });
            form.modal.modal('show');
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