define([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'models/value',
    'models/concept-parents',
    'views/rdm/modals/value-form',
    'views/rdm/modals/related-concept-form',
    'views/rdm/modals/related-member-form',
    'views/rdm/modals/manage-parent-form',
    'views/rdm/modals/import-concept-form',
    'views/rdm/modals/add-child-form',
    'views/rdm/modals/add-image-form',
    'views/concept-graph'
], function($, Backbone, arches, ConceptModel, ValueModel, ConceptParentModel, ValueEditor, RelatedConcept, RelatedMember, ManageParentForm, ImportConcept, AddChildForm, AddImageForm, ConceptGraph) {
    return Backbone.View.extend({
        events: {
            'click .concept-report-content *[data-action="viewconcept"]': 'conceptSelected',
            'click .concept-report-content *[data-action="viewddconcept"]': 'dropdownConceptSelected',
            'click .concept-report-content *[data-action="delete-relationship"]': 'deleteClicked',
            'click .concept-report-content *[data-action="delete-value"]': 'deleteClicked',
            'click .concept-report-content *[data-action="delete-concept"]': 'deleteClicked',
            'click a.add-image-link': 'addImageClicked',
            'click a.edit-value': 'editValueClicked',
            'click .confirm-delete-yes': 'deleteConfirmed',
            'click a[data-toggle="#related-concept-form"]': 'addRelatedConceptClicked',
            'click a[data-toggle="#related-member-form"]': 'addRelatedMemberClicked',
            'click a[data-toggle="#add-concept-form"]': 'addChildConcept',
            'click a[data-toggle="#add-top-concept-form"]': 'addChildConcept',
            'click a[data-toggle="#manage-parent-form"]': 'manageParentConcepts',
            'click a[data-toggle="#import-concept-form"]': 'importConcept',
        },

        initialize: function(options) {
            this.render();
        },

        render: function() {
            var self = this;
            var conceptid = this.model.get('id');
            var showGraph = self.$el.find(".concept-graph").is(":visible");
            
            if (this.model.get('in_use')) {
                self.in_use = true;
            }

            self.inuse = false;
            self.$el.find('.concept-report-loading').removeClass('hidden');
            self.$el.find('.concept-report-content').addClass('hidden');

            if (this.xhr){
                this.xhr.abort();
            }

            self.displayInUse = function() {
                if (self.in_use === true) {
                    self.cannot_delete_modal = self.$el.find('.cannot-delete-modal');
                    self.cannot_delete_modal.modal('show');
                    self.in_use = false;
                }
            }

            this.xhr = $.ajax({
                in_use: self.inuse,
                url: arches.urls.concept.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', conceptid),
                data: {
                    'f': 'html',
                    'mode': this.mode
                },
                success: function(response) {
                    self.$el.find('.concept-report-loading').addClass('hidden');
                    self.$el.html(response);

                    var data = self.$el.find('div[name="modeldata"]').data();
                    self.model.set(data);

                    if (self.model.get('id')) {
                        if (self.$el.find(".concept-graph").length > 0) {
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
                    }
                },
                complete: self.displayInUse
            });
        },

        deleteClicked: function(e) {
            var self = this;
            var data = $(e.target).data();

            this.confirm_delete_modal = this.$el.find('.confirm-delete-modal');
            this.confirm_delete_modal_yes = this.confirm_delete_modal.find('.confirm-delete-yes');
            this.confirm_delete_modal_yes.removeAttr('disabled');
            this.confirm_delete_modal_yes.data('id', data.id);
            this.confirm_delete_modal_yes.data('nodetype', data.nodetype);
            this.confirm_delete_modal_yes.data('action', data.action);
            this.confirm_delete_modal_yes.data('category', data.category);

            this.confirm_delete_modal.find('.modal-title').text($(e.target).attr('title'));
            this.confirm_delete_modal.find('.modal-body [name="warning-text"]').text(data.message);
            this.confirm_delete_modal.find('.modal-body [name="additional-info"]').text('');            
            this.confirm_delete_modal.modal('show');

            if (data.action === 'delete-concept'){
                this.confirm_delete_modal_yes.attr('disabled', 'disabled');
                $.ajax({
                    url: arches.urls.confirm_delete.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', data.id),
                    success: function(response) {
                        self.confirm_delete_modal_yes.removeAttr('disabled');
                        self.confirm_delete_modal.find('.modal-body [name="additional-info"]').html(response);
                    }
                });                
            }

        },

        conceptSelected: function(e) {
            var data = $(e.target).data();
            this.trigger('conceptSelected', data.conceptid);
        },

        dropdownConceptSelected: function(e) {
            var data = $(e.target).data();
            this.trigger('dropdownConceptSelected', data.conceptid);
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

        addRelatedMemberClicked: function(e){
            this.model.reset();
            var modal = new RelatedMember({
                el: $('#related-member-form')[0],
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

        importConcept: function(e){
            var self = this;
            this.model.reset();
            var modal = new ImportConcept({
                el: $('#import-concept-form')[0],
                model: this.model
            });
            modal.modal.modal('show');

            modal.on({
                'conceptsImported': function(){
                    self.trigger('conceptsImported');
                }
            });
        },    

        addImageClicked: function (e) {
            this.model.reset();
            var self = this;
            var form = new AddImageForm({
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
            var title = modal.find('.modal-title').text();
            this.model.reset();

            if (data.action === 'delete-concept') {
                modal.find('h4').text(' ' + title);
                modal.find('.modal-title').addClass('loading');    
                            
                model = new ConceptModel(data)
                self.model.set('subconcepts', [model]);

                self.model.delete(function(){
                    modal.find('h4').text(title);
                    modal.find('.modal-title').removeClass('loading');
                    modal.modal('hide');
                    $('.modal-backdrop.fade.in').remove();  // a hack for now
                }, self);
            }else{
                modal.on('hidden.bs.modal', function () {
                    var model;

                    if (data.action === 'delete-value') {
                        model = new ValueModel(data);
                        model.delete();
                        self.render();
                    }
                    if (data.action === 'delete-relationship') {
                        model = new ConceptModel(data);
                        self.model.set('relatedconcepts', [model]);
                        self.model.delete();
                    }

                });
                modal.modal('hide');                
            }            
        }
    });
});