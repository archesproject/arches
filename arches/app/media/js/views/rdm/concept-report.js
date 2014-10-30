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
            var data = $(e.target).data();

            this.$el.find('.confirm-delete-modal .modal-title').text($(e.target).attr('title'));
            this.$el.find('.confirm-delete-modal .modal-body').text(data.message);
            this.$el.find('.confirm-delete-yes').data('id', data.id);
            this.$el.find('.confirm-delete-yes').data('action', data.action);
            this.$el.find('.confirm-delete-yes').data('category', data.category);
            this.$el.find('.confirm-delete-modal').modal('show');
        },

        conceptSelected: function(e) {
            var data = $(e.target).data();

            this.trigger('conceptSelected', data.conceptid);
        },

        addChildConcept: function(e){
            var form = new AddChildForm({
                el: $('#add-child-form')[0],
                model: this.model
            });

            form.modal.modal('show');
        },

        addRelatedConceptClicked: function(e){
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