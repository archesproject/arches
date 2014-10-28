define(['jquery', 'backbone', 'arches', 'views/concept-search', 'models/concept', 'models/value'], function ($, Backbone, arches, ConceptSearch, ConceptModel, ValueModel) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = $('#add-scheme-form');
            this.modal.on('hidden.bs.modal', function () {
                self.$el.find("input[type=text], textarea").val("");
            });
            // test to see if select2 has already been applied to the dom
            if (! this.modal.find('.select2').attr('id')){
                this.select2 = this.modal.find('.select2').select2();                
            }
            this.modal.validate({
                ignore: null,
                rules: {
                    label: "required",
                    language_dd: "required"
                },
                submitHandler: function(form) {
                    var model = new ConceptModel({
                        id: '00000000-0000-0000-0000-000000000003'
                    })
                    var label = new ValueModel({
                        value: $(form).find("[name=label]").val(),
                        language: $(form).find("[name=language_dd]").val(),
                        category: 'label',
                        datatype: 'text',
                        type: 'prefLabel'
                    });
                    var subconcept = new ConceptModel({
                        values: [label],
                        relationshiptype: 'has collection'
                    });
                    model.set('subconcepts', [subconcept]);
                    model.save(function() {
                        var modal = self.$el.find('#add-scheme-form');
                        this.modal.modal('hide');
                        $('.modal-backdrop.fade.in').remove();  // a hack for now
                        self.trigger('conceptSchemeAdded');
                    }, self);
                }
            });
        }
    });
});