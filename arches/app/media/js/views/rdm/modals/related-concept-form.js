define(['jquery', 'backbone', 'arches', 'views/concept-search', 'models/concept'], function ($, Backbone, arches, ConceptSearch, ConceptModel) {
    return ConceptSearch.extend({

        events: {
            'click .modal-footer .savebtn': 'save'
        },

        initialize: function(){
            ConceptSearch.prototype.initialize.apply(this, arguments);
            this.modal = $('#related-concept-form');
        },
        
		save: function(){
            if (this.searchbox.val() !== ''){
                var modal = this.$el.find('#related-concept-form');
                var relatedConcept = new ConceptModel({
                    id: this.searchbox.val()
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