define(['jquery', 'backbone', 'models/concept', 'models/value'], function($, Backbone, ConceptModel, ValueModel) {
    return Backbone.View.extend({

        initialize: function(e){
            var self = this;
            this.modal = this.$el.find('.modal');
            this.modal.on('hidden.bs.modal', function() {
                self.$el.find('input[type=text], textarea').val('');
            });

            this.select2 = this.$el.find('[name=language_dd]').select2({
                minimumResultsForSearch: -1
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

                    var collection = new ConceptModel({
                        legacyoid: $(form).find('[name=label]').val(),
                        values: [label],
                        nodetype: 'Collection'
                    });

                    self.modal.on('hidden.bs.modal', function(e) {
                        collection.save(function(response, status) {
                            self.trigger('collectionAdded', response.responseJSON);
                        }, self);
                    });
                    self.modal.modal('hide');

                    return false;
                }
            });
        }
    });
});