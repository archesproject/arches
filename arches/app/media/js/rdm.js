require([
    'jquery',
    'backbone',
    'arches',
    'models/concept',
    'models/value',
    'views/concept-tree',
    'views/value-editor',
    'jquery-validate',
], function($, Backbone, arches, ConceptModel, ValueModel, ConceptTree, ValueEditor) {
    $(document).ready(function() {
        var activeConcept = new ConceptModel();
        new(Backbone.View.extend({
            el: $('body')[0],
            activeConcept: activeConcept,
            conceptTree: new ConceptTree({
                el: $('#jqtree')[0],
                model: activeConcept
            }),
            events: {
                'click #concept_report': 'reportClicked',
                'click a.edit-value': 'editValueClicked',
                'click #confirm_delete_yes': 'deleteConfirmed'
            },

            initialize: function() {
                var self = this;

                self.activeConcept.on('change', function() {
                    window.history.pushState({}, "conceptid", self.activeConcept.get('id'));
                    self.loadConceptReport();
                });

                self.conceptTree.on('conceptMoved', function(conceptid) {
                    if (self.activeConcept.get('id') === conceptid) {
                        self.loadConceptReport();
                    }
                });

                // ADD CHILD CONCEPT EDITOR 
                $('#conceptmodal').validate({
                    ignore: null, // required so that the select2 dropdowns will be visible to the validate plugin
                    rules: {
                        // element_name: value
                        label: "required",
                        language_dd: "required"
                    },
                    submitHandler: function(form) {
                        var data = {
                                label: $(form).find("[name=label]").val(),
                                note: $(form).find("[name=note]").val(),
                                language: $(form).find("[name=language_dd]").select2('val'),
                                parentconceptid: self.activeConcept.get('id')
                            },
                            concept = new ConceptModel(data);
                        concept.save(function(data) {
                            $('#conceptmodal').modal('hide');
                            self.conceptTree.render();
                        });
                    }
                });
            },

            loadConceptReport: function() {
                var conceptid = this.activeConcept.get('id');
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
            },

            reportClicked: function(e) {
                var data = $(e.target).data();
                if (data.action === 'delete' || data.action === 'delete_concept') {
                    $('#confirm_delete_modal .modal-title').text($(e.target).attr('title'));
                    $('#confirm_delete_modal .modal-body').text(data.message);
                    $('#confirm_delete_modal').modal('show');
                    $('#confirm_delete_yes').data('id', data.id);
                    $('#confirm_delete_yes').data('action', data.action);
                }

                if (data.action === 'viewconcept') {
                    this.activeConcept.set({
                        id: data.conceptid
                    });
                }
            },

            editValueClicked: function(e) {
                var self = this,
                    data = $.extend({
                        conceptid: this.activeConcept.get('id')
                    }, $(e.target).data()),
                    model = new ValueModel(data),
                    editor = new ValueEditor({
                        el: $(data.target)[0],
                        model: model
                    });

                editor.on('submit', function() {
                    model.save(function() {
                        self.conceptTree.render();
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
                        self.loadConceptReport();
                    });
                }
                if (data.action === 'delete_concept') {
                    model = new ConceptModel(data);
                    model.delete(function(data) {
                        $('#confirm_delete_modal').modal('hide');
                        self.conceptTree.render();
                    });
                }
            }
        }))();
    });
});