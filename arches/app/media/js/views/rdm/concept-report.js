define([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'models/value',
    'views/rdm/modals/value-form',
    'views/rdm/modals/related-concept-form'
], function($, Backbone, arches, ConceptModel, ValueModel, ValueEditor, RelatedConcept) {
    return Backbone.View.extend({
        events: {
            'click .concept-report-content *': 'contentClick',
            'click a.edit-value': 'editValueClicked',
            'click .confirm-delete-yes': 'deleteConfirmed'
        },

        initialize: function() {
            var self = this;

            self.model.on('change', function() {
                self.render();
            });

            self.render();
        },

        render: function() {
            var self = this,
                conceptid = this.model.get('id');
            if (conceptid) {
                self.$el.find('.concept-report-loading').removeClass('hidden');
                self.$el.find('.concept-report-content').addClass('hidden');
                $.ajax({
                    url: '../Concepts/' + conceptid + '?f=html',
                    success: function(response) {
                        self.$el.find('.concept-report-loading').addClass('hidden');
                        self.$el.html(response);
                        self.$el.find('#conceptmodal').validate({
                            ignore: null,
                            rules: {
                                label: "required",
                                language_dd: "required"
                            },
                            submitHandler: function(form) {
                                var childConcept = new ConceptModel({
                                        label: $(form).find("[name=label]").val(),
                                        note: $(form).find("[name=note]").val(),
                                        language: $(form).find("[name=language_dd]").val(),
                                        parentconceptid: self.model.get('id')
                                    });
                                childConcept.save(function() {
                                    self.$el.find('#conceptmodal').modal('hide');
                                    self.$el.find("input[type=text], textarea").val("");
                                    self.trigger('conceptAdded', childConcept);
                                });
                            }
                        });
                        var add_related_concept_modal = new RelatedConcept({ 
                            el: $('#related-concept-form')[0],
                            model: self.model
                        });   
                    }
                });
            }
        },

        contentClick: function(e) {
            var self = this,
                data = $(e.target).data();
            if (data.action === 'delete' || data.action === 'delete_concept') {
                self.$el.find('.confirm-delete-modal .modal-title').text($(e.target).attr('title'));
                self.$el.find('.confirm-delete-modal .modal-body').text(data.message);
                self.$el.find('.confirm-delete-yes').data('id', data.id);
                self.$el.find('.confirm-delete-yes').data('action', data.action);
                self.$el.find('.confirm-delete-modal').modal('show');
            }

            if (data.action === 'viewconcept') {
                this.model.set({
                    id: data.conceptid
                });
            }
        },

        editValueClicked: function(e) {
            var self = this,
                data = $.extend({
                    conceptid: this.model.get('id')
                }, $(e.target).data()),
                model = new ValueModel(data),
                editor = new ValueEditor({
                    el: this.$el.find('#value-form')[0],
                    model: model
                });

            editor.on('save', function() {
                self.render();
                self.trigger('valueSaved', model);
            });
        },

        deleteConfirmed: function(e) {
            var self = this,
                data = $(e.target).data(),
                modal = self.$el.find('.confirm-delete-modal'),
                Model, model, eventName;

            modal.on('hidden.bs.modal', function () {
                if (data.action === 'delete') {
                    model = new ValueModel(data);
                    eventName = 'valueDeleted';
                }
                if (data.action === 'delete_concept') {
                    model = new ConceptModel(data);
                    model.set('id', self.model.get('id'));
                    eventName = 'conceptDeleted';
                }

                model.delete(function() {
                    self.render();
                    self.trigger(eventName, model);
                });
            });
            modal.modal('hide');
        }
    });
});