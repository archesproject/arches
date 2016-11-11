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
    'views/rdm/modals/import-scheme-form',
    'views/base-manager',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport, ConceptSearch, AddSchemeForm, ExportSchemeForm, DeleteSchemeForm, ImportSchemeForm, BaseManagerView) {
    $(document).ready(function() {
        window.onpopstate = function(event) {
          //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
          //window.location = document.location;
        };

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
            model: concept,
            mode: ''
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
                if(concept.get('nodetype') === 'ConceptScheme'){
                    conceptTree.render();
                }
                conceptReport.render();
                concept.reset()
            },
            'delete': function(){
                if(concept.get('nodetype') === 'ConceptScheme'){
                    conceptTree.render();
                }
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
                conceptReport.mode = '';
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
            'dropdownConceptSelected': function(conceptid) {
                concept.clear();
                concept.set('id', conceptid);

                conceptReport.render('dropdown');
            },
            'parentsChanged': function() {
                //conceptTree.render();
                conceptReport.render();
            },
            'conceptsImported': function() {
                conceptReport.render();
            }
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
                    window.location.reload();
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
                el: $('#delete-scheme-form'),
                model: null
            });
            form.modal.modal('show');
            form.on({
                'conceptSchemeDeleted': function(){
                    window.location.reload();
                }
            })
        });

        $('a[data-toggle="#import-scheme-form"]').on( "click", function(){
            var self = this;
            var form = new ImportSchemeForm({
                el: $('#import-scheme-form'),
                model: concept
            });
            form.modal.modal('show');
            form.on({
                'conceptSchemeAdded': function(){
                    window.location.reload();
                }
            })
        });

        new BaseManagerView();
    });
});
