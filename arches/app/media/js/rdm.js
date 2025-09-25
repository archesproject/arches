import $ from 'jquery';
import arches from 'arches';
import Backbone from 'backbone';
import ConceptModel from 'models/concept';
import ConceptTree from 'views/rdm/concept-tree';
import ConceptReport from 'views/rdm/concept-report';
import ConceptSearch from 'views/concept-search';
import AddSchemeForm from 'views/rdm/modals/add-scheme-form';
import ExportSchemeForm from 'views/rdm/modals/export-scheme-form';
import DeleteSchemeForm from 'views/rdm/modals/delete-scheme-form';
import ImportSchemeForm from 'views/rdm/modals/import-scheme-form';
import AddCollectionForm from 'views/rdm/modals/add-collection-form';
import DeleteCollectionForm from 'views/rdm/modals/delete-collection-form';
import BaseManagerView from 'views/base-manager';
import JsonErrorAlertViewModel from 'viewmodels/alert-json';
import 'jquery-validate';


var RDMView = BaseManagerView.extend({
    initialize: function(options){
        // allow select2 to retain focus when used in a bootsrap modal
        // see: https://select2.org/troubleshooting/common-problems#select2-does-not-function-properly-when-i-use-it-inside-a-bootst
        $.fn.modal.Constructor.prototype.enforceFocus = function() {};
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
            mode: 'semantic',
            viewModel: this.viewModel
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
                dropdownTree.render();
                conceptReport.render();
                concept.reset();
            },
            'delete': function(){
                conceptTree.render();
                dropdownTree.render();
                conceptReport.render();
                concept.reset();
            },
            'collection_created': function() {
                //window.location.reload();
                dropdownTree.render();
            },
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
                conceptTree.render();
                conceptReport.render();
            },
            'conceptsImported': function() {
                conceptReport.render();
            }
        });

        conceptsearch.on("select2:selecting", function(e) {
            concept.clear();
            concept.set('id', e.params.args.data.id);
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
            var form = new AddSchemeForm({
                el: $('#add-scheme-form')
            });
            form.modal.modal('show');
            form.on({
                'conceptSchemeAdded': function(newScheme){
                    conceptTree.render();
                    concept.set('id', newScheme.id);
                    conceptReport.render();
                }
            });
        });

        $('a[data-toggle="#export-scheme-form"]').on( "click", function(){
            var form = new ExportSchemeForm({
                el: $('#export-scheme-form')
            });
            form.modal.modal('show');
        });

        $('a[data-toggle="#delete-scheme-form"]').on( "click", function(){
            var form = new DeleteSchemeForm({
                el: $('#delete-scheme-form'),
                model: null,
                viewModel: this.viewModel
            });
            form.modal.modal('show');
            form.on({
                'conceptSchemeDeleted': function(){
                    window.location = arches.urls.rdm;
                }
            });
        }.bind(this));

        $('a[data-toggle="#import-scheme-form"]').on( "click", function(){
            var self = this;
            var form = new ImportSchemeForm({
                el: $('#import-scheme-form'),
                model: concept,
                viewModel: this.viewModel
            });
            form.modal.modal('show');
            form.on({
                'conceptSchemeAdded': function(response, status){
                    if (status === 'success'){
                        conceptTree.render();
                        concept.set('id', response.responseJSON.id);
                        conceptReport.render();

                    } else {
                        self.viewModel.alert(new JsonErrorAlertViewModel('ep-alert-red', response.responseJSON));
                    }
                }
            });
        }.bind(this));

        $('a[data-toggle="#add-collection-form"]').on( "click", function(){
            var form = new AddCollectionForm({
                el: $('#add-collection-form')
            });
            form.modal.modal('show');
            form.on({
                'collectionAdded': function(newCollection){
                    dropdownTree.render();
                    concept.set('id', newCollection.id);
                    conceptReport.render();
                }
            });
        });

        $('a[data-toggle="#delete-collection-form"]').on( "click", function(){
            var form = new DeleteCollectionForm({
                el: $('#delete-collection-form'),
                model: null
            });
            form.modal.modal('show');
            form.on({
                'collectionDeleted': function(){
                    dropdownTree.render();
                }
            });
        });

        $('a[data-toggle="#export-all-collections"]').on( "click", function(){
            window.open(arches.urls.export_concept_collections,'_blank');
        });


        BaseManagerView.prototype.initialize.call(this, options);
    }
});

export default new RDMView();
