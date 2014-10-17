define(['jquery', 'backbone', 'arches', 'select2'], function ($, Backbone, arches, Select2) {
    return Backbone.View.extend({

        events: {
            'click .modal-footer .savebtn': 'saveRelated'
        },

        initialize: function() {
        	var self = this;

            this.select2 = this.$el.find('input.concept_search_widget').select2({
				placeholder: "Add search terms...",
				multiple: false,
				maximumselectionsize: 1,
				minimumInputLength: 2,
				ajax: {
					url: arches.urls.concept_search,
					dataType: 'json',
					data: function (term, page) {
						return {
							q: term, // search term
							page_limit: 30
						};
					},
					results: function (data, page) {
						var	results = [];
						$.each(data.hits.hits, function(){
							results.push({
								id: this._source.conceptid,
								text: this._source.value,
								scheme: this._type
							});
						}, this);
						return {results: results};
					}
				},
				formatResult:function(result, container, query, escapeMarkup){
					var markup=[];
            		window.Select2.util.markMatch(result.text, query.term, markup, escapeMarkup);
            		var formatedresult = '<span class="concept_result">' + markup.join("")  + '</span><i class="concept_result_schemaname">(' + result.scheme + ')</i>';
            		return formatedresult;
				},
				escapeMarkup: function(m) { return m; }
			}).on("select2-selecting", function(e, el) {
				self.trigger("select2-selecting", e, el);
			});
        },

		saveRelated: function(){
			$.ajax({
                type: "POST",
                url: arches.urls.concept_relation.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.model.get('id')),
                data: JSON.stringify({
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