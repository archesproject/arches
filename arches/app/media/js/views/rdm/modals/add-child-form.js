define(['jquery', 'backbone', 'arches', 'views/concept-search', 'models/concept', 'models/value'], function ($, Backbone, arches, ConceptSearch, ConceptModel, ValueModel) {
    return Backbone.View.extend({


        initialize: function(e){
            if (! this.rendered){
                this.render();
            }
        },

        render: function(e){
            var self = this;
            this.rendered = true; 

            this.modal = this.$el.find('form');
            this.modal.on('hidden.bs.modal', function () {
                self.$el.find("input[type=text], textarea").val("");
            });

            this.modal.find('.select2').select2({
                minimumResultsForSearch: 10,
                maximumSelectionSize: 1
            });                

            this.modal.validate({
                ignore: null,
                rules: {
                    label: "required",
                    language_dd: "required"
                },
                submitHandler: function(form) {
                    var label = new ValueModel({
                        value: $(form).find("[name=label]").val(),
                        language: $(form).find("[name=language_dd]").val(),
                        category: 'label',
                        datatype: 'text',
                        type: 'prefLabel'
                    });
                    var note = new ValueModel({
                        value: $(form).find("[name=note]").val(),
                        language: $(form).find("[name=language_dd]").val(),
                        category: 'note',
                        datatype: 'text',
                        type: 'scopeNote'
                    });
                    var subconcept = new ConceptModel({
                        values: [label, note],
                        relationshiptype: $(form).find("[name=relationshiptype_dd]").val()
                    });
                    self.model.set('values', []);
                    self.model.set('subconcepts', [subconcept]);

                    self.modal.on('hidden.bs.modal', function () {
                        self.model.save();
                    });
                    self.modal.modal('hide');
                }
            });
        }
    });
});