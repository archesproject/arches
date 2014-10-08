define([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'models/value',
    'views/value-editor'
], function($, Backbone, arches, ConceptModel, ValueModel, ValueEditor) {
    return Backbone.View.extend({
        events: {
            'click': 'click',
            'click a.edit-value': 'editValueClicked',
            'click #confirm_delete_yes': 'deleteConfirmed'
        },

        initialize: function() {
            var self = this;

            self.model.on('change', function() {
                self.render();
            });

            self.render();
        },

        render: function() {
            var conceptid = this.model.get('id');
            if (conceptid) {
                $('#concept_report_loading').removeClass('hidden');
                $('#concept_report').addClass('hidden');
                $.ajax({
                    url: '../Concepts/' + conceptid + '?f=html',
                    success: function(response) {
                        $('#concept_report_loading').addClass('hidden');
                        $('#concept_report').removeClass('hidden');
                        $('#concept_report').html(response);
                    }
                });
            }
        },

        click: function(e) {
            var data = $(e.target).data();
            if (data.action === 'delete' || data.action === 'delete_concept') {
                $('#confirm_delete_modal .modal-title').text($(e.target).attr('title'));
                $('#confirm_delete_modal .modal-body').text(data.message);
                $('#confirm_delete_modal').modal('show');
                $('#confirm_delete_yes').data('id', data.id);
                $('#confirm_delete_yes').data('action', data.action);
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
                    el: $(data.target)[0],
                    model: model
                });

            editor.on('submit', function() {
                model.save(function() {
                    self.trigger('valueSaved', model);
                });
            });
        },

        deleteConfirmed: function(e) {
            var self = this,
                data = $(e.target).data(),
                model;
            if (data.action === 'delete') {
                model = new ValueModel(data);
                model.delete(function() {
                    $('#confirm_delete_modal').modal('hide');
                    self.render();
                    self.trigger('valueDeleted', model);
                });
            }
            if (data.action === 'delete_concept') {
                model = new ConceptModel(data);
                model.delete(function(data) {
                    $('#confirm_delete_modal').modal('hide');
                    self.trigger('conceptDeleted', model);
                });
            }
        }
    });
});