define(['jquery', 'backbone', 'models/concept', 'models/value', 'views/concept-scheme-group-dd'], function ($, Backbone, ConceptModel, ValueModel, ConceptSchemeGroupDD) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = this.$el.find('.modal');
            this.modal.on('hidden.bs.modal', function () {
                self.$el.find('input[type=text], textarea').val('');
            });

            this.select2 = this.$el.find('[name=language_dd]').select2({
                minimumResultsForSearch: -1
            });                

            this.conceptschemegroupdd = new ConceptSchemeGroupDD({
                el: this.$el
            });

            this.modal.validate({
                ignore: null,
                rules: {
                    label: 'required',
                    language_dd: 'required',
                    scheme_group_dd: 'required'
                },
                submitHandler: function(form) {
                    var label = new ValueModel({
                        value: $(form).find('[name=label]').val(),
                        language: $(form).find('[name=language_dd]').val(),
                        category: 'label',
                        type: 'prefLabel'
                    });
                    var note = new ValueModel({
                        value: $(form).find('[name=note]').val(),
                        language: $(form).find('[name=language_dd]').val(),
                        category: 'note',
                        type: 'scopeNote'
                    });
                    var conceptscheme = new ConceptModel({
                        legacyoid: $(form).find('[name=label]').val(),
                        values: [label, note],
                        relationshiptype: 'narrower',
                        nodetype: 'ConceptScheme'
                    });
                    
                    var conceptschemegroup = self.conceptschemegroupdd.getSchemeGroupModelFromSelection($(form).find('[name=language_dd]').val());
                    conceptschemegroup.set('subconcepts',[conceptscheme]);

                    conceptschemegroup.save(function() {
                        self.modal.modal('hide');
                        $('.modal-backdrop.fade.in').remove();  // a hack for now
                        self.trigger('conceptSchemeAdded');
                    }, self);

                    return false;
                }
            });
        }
    });
});