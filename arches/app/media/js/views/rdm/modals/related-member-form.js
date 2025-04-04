import $ from 'jquery';
import Backbone from 'backbone';
import ConceptSearch from 'views/concept-search';
import ConceptModel from 'models/concept';


export default ConceptSearch.extend({

    events: {
        'click .modal-footer .savebtn': 'save'
    },

    initialize: function(){
        ConceptSearch.prototype.initialize.apply(this, arguments);
        this.modal = this.$el.find('.modal');
        this.relationshiptype = this.modal.find('#related-relation-type').select2({
            minimumResultsForSearch: 10,
            maximumSelectionSize: 1
        });
    },
    
    save: function(){
        var self = this;
        if (this.searchbox.val() !== ''){
            var relatedConcept = new ConceptModel({
                id: this.searchbox.val(),
                relationshiptype: this.relationshiptype.val()
            });
            this.model.set('relatedconcepts', [relatedConcept]);

            this.modal.on('hidden.bs.modal', function(e) {
                self.model.save();
            });
            this.modal.modal('hide');
        }
    }
});
