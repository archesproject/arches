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
    'views/rdm/modals/add-collection-form',
    'views/rdm/modals/delete-collection-form',
    'views/base-manager',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ConceptTree, ConceptReport, ConceptSearch, 
    AddSchemeForm, ExportSchemeForm, DeleteSchemeForm, ImportSchemeForm, AddCollectionForm, DeleteCollectionForm, BaseManagerView) {
    $(document).ready(function() {
        window.onpopstate = function(event) {
          //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
          //window.location = document.location;
        };

        var mode = 'semantic';

        // Models and views
        var concept = new ConceptModel({
            id: $('#selected-conceptid').val()
        });
        var conceptTree = new ConceptTree({
            el: $('#jqtree')[0],
            model: concept,
            url: arches.urls.concept_tree + 'semantic'
        });
        var dropdownTree = new ConceptTree({
            el: $('#ddtree')[0],
            model: concept,
            url: arches.urls.concept_tree + 'collections'
        });
        var conceptReport = new ConceptReport({
            el: $('#concept_report')[0],
            model: concept,
            mode: 'semantic'
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
                conceptReport.mode = 'semantic';
                conceptReport.render();
            }
        });

        dropdownTree.on({
            'conceptMoved': function() {
                conceptReport.render();
            },
            'conceptSelected': function(conceptid){
                concept.clear();
                concept.set('id', conceptid);
                conceptReport.mode = 'collections';
                conceptReport.render();
            }
        });

        conceptReport.on({
            'conceptSelected': function(conceptid) {
                concept.clear();
                concept.set('id', conceptid);

                conceptReport.mode = 'semantic';
                conceptReport.render();
            },
            'dropdownConceptSelected': function(conceptid) {
                concept.clear();
                concept.set('id', conceptid);

                conceptReport.mode = 'collections';
                conceptReport.render();
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


        $('a[href="#rdm-panel"]').on( "click", function(){
            var selectedNode = conceptTree.tree.tree('getSelectedNode');
            concept.clear();
            concept.set('id', selectedNode.id || '');
           
            conceptReport.mode = 'semantic';
            conceptReport.render();
        });

        $('a[href="#dropdown-panel"]').on( "click", function(){
            var selectedNode = dropdownTree.tree.tree('getSelectedNode');
            concept.clear();
            concept.set('id', selectedNode.id || '');
            
            conceptReport.mode = 'collections';
            conceptReport.render();
        });

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

        $('a[data-toggle="#add-collection-form"]').on( "click", function(){
            var self = this;
            var form = new AddCollectionForm({
                el: $('#add-collection-form')
            });
            form.modal.modal('show');
            form.on({
                'collectionAdded': function(){
                    window.location.reload();
                }
            })
        });

        $('a[data-toggle="#delete-collection-form"]').on( "click", function(){
            var self = this;
            var form = new DeleteCollectionForm({
                el: $('#delete-collection-form'),
                model: null
            });
            form.modal.modal('show');
            form.on({
                'collectionDeleted': function(){
                    //window.location.reload();
                }
            })
        });

        $('a[data-toggle="#export-all-collections"]').on( "click", function(){
            window.open(arches.urls.export_concept_collections,'_blank');
        });

        new BaseManagerView();
    });
});
