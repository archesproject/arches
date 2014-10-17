define(['jquery', 'backbone', 'arches', 'views/concept-search'], function ($, Backbone, arches, ConceptSearch) {
    return ConceptSearch.extend({

        events: {
            'click .modal-footer .savebtn': 'saveRelated'
        },

		saveRelated: function(){
			var self = this;
			$.ajax({
                type: "POST",
                url: arches.urls.concept.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.model.get('id')),
                data: JSON.stringify({
                	'action': 'manage_related_concept',
                    'related_concept': this.select2.val()
                }),
                success: function() {
                    var data = JSON.parse(this.data);
                    console.log(data)
                    self.trigger('conceptMoved', data.conceptid);
                }
            });
		}

    });
});