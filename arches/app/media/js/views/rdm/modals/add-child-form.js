import $ from 'jquery';
import Backbone from 'backbone';
import ConceptSearch from 'views/concept-search';
import ConceptModel from 'models/concept';
import ValueModel from 'models/value';


export default Backbone.View.extend({

    initialize: function(e){
        var self = this;
        this.modal = this.$el.find('form');
        this.modal.on('hidden.bs.modal', function() {
            self.$el.find("input[type=text], textarea").val("");
            // self.trigger('conceptAdded', subconcept);
            // self.render();
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
                    type: 'prefLabel'
                });
                var note = new ValueModel({
                    value: $(form).find("[name=note]").val(),
                    language: $(form).find("[name=language_dd]").val(),
                    category: 'note',
                    type: 'scopeNote'
                });
                var subconcept = new ConceptModel({
                    values: [label, note],
                    relationshiptype: $(form).find("[name=relationshiptype_dd]").val(),
                    nodetype: 'Concept'
                });
                self.model.set('values', []);
                self.model.set('subconcepts', [subconcept]);

                self.modal.on('hidden.bs.modal', function() {
                    self.model.save();
                });
                self.modal.modal('hide');
            }
        });
    }
});
