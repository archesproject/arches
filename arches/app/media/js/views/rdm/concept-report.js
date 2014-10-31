define([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'models/value',
    'models/concept-parents',
    'views/rdm/modals/value-form',
    'views/rdm/modals/related-concept-form',
    'views/rdm/modals/manage-parent-form',
    'views/rdm/modals/add-child-form',
    'views/rdm/modals/add-image-form',
    'views/concept-graph'
], function($, Backbone, arches, ConceptModel, ValueModel, ConceptParentModel, ValueEditor, RelatedConcept, ManageParentForm, AddChildForm, AddImageForm, ConceptGraph) {
    return Backbone.View.extend({
        events: {
            'click .concept-report-content *[data-action="viewconcept"]': 'conceptSelected',
            'click .concept-report-content *[data-action="delete-relationship"]': 'deleteClicked',
            'click .concept-report-content *[data-action="delete-value"]': 'deleteClicked',
            'click .concept-report-content *[data-action="delete-concept"]': 'deleteClicked',
            'click a.add-image-link': 'addImageClicked',
            'click a.edit-value': 'editValueClicked',
            'click .confirm-delete-yes': 'deleteConfirmed',
            'click a[data-toggle="#related-concept-form"]': 'addRelatedConceptClicked',
            'click a[data-toggle="#add-concept-form"]': 'addChildConcept',
            'click a[data-toggle="#manage-parent-form"]': 'manageParentConcepts'
        },

        initialize: function() {
            this.render();
        },

        render: function() {
            var self = this;
            var conceptid = this.model.get('id');
            var showGraph = self.$el.find(".concept-graph").is(":visible");

            if (conceptid) {
                self.$el.find('.concept-report-loading').removeClass('hidden');
                self.$el.find('.concept-report-content').addClass('hidden');


                $.ajax({
                    url: '../Concepts/' + conceptid + '?f=html',
                    success: function(response) {
                        self.$el.find('.concept-report-loading').addClass('hidden');
                        self.$el.html(response);
                        
                        //Toggle Concept Heirarchy.  
                        self.$el.find(".graph-toggle").click(function(){
                            self.$el.find(".concept-tree").toggle(300);
                            self.$el.find(".concept-graph").toggle(300);
                            self.$el.find(".graph-toggle").toggle();
                        });
                        new ConceptGraph({
                            el: self.$el.find(".concept-graph")
                        });
                        if (showGraph) {
                            self.$el.find(".graph-toggle").toggle();
                            self.$el.find(".concept-tree").toggle(0);
                            self.$el.find(".concept-graph").toggle(0);
                        }
                    }
                });
            }
        },

        deleteClicked: function(e) {
            var self = this;
            var data = $(e.target).data();

            confirm_delete_modal = this.$el.find('.confirm-delete-modal');
            confirm_delete_modal_yes = confirm_delete_modal.find('.confirm-delete-yes');

            confirm_delete_modal_yes.data('id', data.id);
            confirm_delete_modal_yes.data('action', data.action);
            confirm_delete_modal_yes.data('category', data.category);

            confirm_delete_modal.find('.modal-title').text($(e.target).attr('title'));
            confirm_delete_modal.find('.modal-body [name="warning-text"]').text(data.message);
            confirm_delete_modal.find('.modal-body [name="additional-info"]').text('');            
            confirm_delete_modal.modal('show');

            if (data.action === 'delete-concept'){
                $.ajax({
                    url: arches.urls.confirm_delete.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', data.id),
                    success: function(response) {
                        confirm_delete_modal.find('.modal-body [name="additional-info"]').html(response);
                    }
                });                
            }

        },

        conceptSelected: function(e) {
            var data = $(e.target).data();

            this.trigger('conceptSelected', data.conceptid);
        },

        addChildConcept: function(e){
            this.model.reset();
            var form = new AddChildForm({
                el: $('#add-child-form')[0],
                model: this.model
            });

            form.modal.modal('show');
        },

        addRelatedConceptClicked: function(e){
            this.model.reset();
            var modal = new RelatedConcept({
                el: $('#related-concept-form')[0],
                model: this.model
            });
            modal.modal.modal('show');
        },

        manageParentConcepts: function(e){
            var self = this;
            var parentmodel = new ConceptParentModel();
            parentmodel.set('id', this.model.get('id'));
            
            var modal = new ManageParentForm({
                el: $('#manage-parent-form')[0],
                model: parentmodel
            });
            modal.modal.modal('show');

            parentmodel.on({
                'save': function(){
                    self.trigger('parentsChanged');
                }
            });
        },        

        addImageClicked: function (e) {
            this.model.reset();
            var self = this,
                form = new AddImageForm({
                    el: this.$el.find('#add-image-form')[0],
                    model: this.model
                });
            form.on('dataChanged', function () {
                self.render();
            });
        },

        editValueClicked: function(e) {
            this.model.reset();
            var data = $.extend({
                    conceptid: this.model.get('id')
                }, 
                $(e.target).data()
            );
            this.model.set('values', [new ValueModel(data)]);
            var editor = new ValueEditor({
                el: this.$el.find('#value-form')[0],
                model: this.model
            });
        },

        deleteConfirmed: function(e) {
            var self = this;
            var data = $(e.target).data();
            var modal = self.$el.find('.confirm-delete-modal');
            this.model.reset();

            modal.on('hidden.bs.modal', function () {
                var model, eventName;

                if (data.action === 'delete-value') {
                    model = new ValueModel(data);
                    self.model.set('values', [model]);
                }
                if (data.action === 'delete-relationship') {
                    model = new ConceptModel(data);
                    self.model.set('relatedconcepts', [model]);
                }
                if (data.action === 'delete-concept') {
                    model = new ConceptModel(data)
                    self.model.set('subconcepts', [model]);
                }

                self.model.delete();
            });
            modal.modal('hide');
        }
    });
});