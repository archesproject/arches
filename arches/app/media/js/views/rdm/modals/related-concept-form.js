define(['jquery', 'backbone', 'arches', 'views/concept-search', 'models/concept'], function ($, Backbone, arches, ConceptSearch, ConceptModel) {
    return ConceptSearch.extend({

        events: {
            'click .modal-footer .savebtn': 'save'
        },

        initialize: function(){
            ConceptSearch.prototype.initialize.apply(this, arguments);
            this.modal = $('#related-concept-form');
            this.conceptsearchbox = this.modal.find('.concept_search_widget');
        },
        
		save: function(){
            if (this.select2.val() !== ''){
                var modal = this.$el.find('#related-concept-form');
                var relatedConcept = new ConceptModel({
                    id: this.select2.val()
                });
                this.model.set('relatedconcepts', [relatedConcept]);
                this.model.save(function() {
                    modal.modal('hide');
                    $('.modal-backdrop.fade.in').remove();  // a hack for now
                });
            }
        }
    });
});