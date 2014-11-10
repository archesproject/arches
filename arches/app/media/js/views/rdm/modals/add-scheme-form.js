define(['jquery', 'backbone', 'models/concept', 'models/value'], function ($, Backbone, ConceptModel, ValueModel) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = this.$el.find('.modal');
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
                    var label = new ValueModel({
                        value: $(form).find("[name=label]").val(),
                        language: $(form).find("[name=language_dd]").val(),
                        category: 'label',
                        datatype: 'text',
                        type: 'prefLabel'
                    });
                    var model = new ConceptModel({
                        values: [label],
                        relationshiptype: 'narrower',
                        nodetype: 'ConceptSchemeGroup'
                    });
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