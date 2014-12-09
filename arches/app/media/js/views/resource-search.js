define(['jquery', 'backbone', 'arches', 'select2'], function ($, Backbone, arches, Select2) {
    return Backbone.View.extend({

        initialize: function(options) {
            $.extend(this, options);
        	this.render();
        },

        render: function(){
            var self = this;
            this.searchbox = this.$el.select2({
                multiple: false,
                maximumselectionsize: 1,
                minimumInputLength: 2,
                ajax: {
                    url: this.getUrl(),
                    dataType: 'json',
                    data: function (term, page) {
                        return {
                            q: term, // search term
                            page_limit: 30
                        };
                    },
                    results: function (data, page) {
                        var results = [];
                        $.each(data.hits.hits, function(){
                            results.push({
                                id: this._source.ids[0],
                                text: this._source.term,
                                scheme_id: this._type,
                                scheme: this._source.options.context
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

        getUrl: function(){
            return arches.urls.search_terms;
        }

    });
});