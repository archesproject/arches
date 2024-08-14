define(['jquery', 'arches', 'backbone', 'views/concept-search', 'models/concept'], function($, arches, Backbone, ConceptSearch, ConceptModel) {
    return ConceptSearch.extend({

        initialize: function(){
            ConceptSearch.prototype.initialize.apply(this, arguments);
            var self = this;
            this.modal = this.$el.find('form');
            this.relationshiptype = this.modal.find('#related-relation-type').select2({
                placeholder: arches.translations.selectAnOption,
                minimumResultsForSearch: 10,
                maximumSelectionSize: 1
            });

            this.modal.validate({
                ignore: null,
                rules: {
                    concept_search_box: 'required',
                    relationtype_dd: 'required'
                },
                submitHandler: function(form) {
                    var relatedConcept = new ConceptModel({
                        id: self.searchbox.val(),
                        relationshiptype: self.relationshiptype.val()
                    });
                    self.model.set('relatedconcepts', [relatedConcept]);

                    self.modal.on('hidden.bs.modal', function(e) {
                        self.model.save();
                    });
                    self.modal.modal('hide');
                }
            });
        }
    });
});