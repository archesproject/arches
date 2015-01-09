define(['jquery', 'backbone', 'arches', 'select2', 'knockout'], function ($, Backbone, arches, Select2, ko) {
    return Backbone.View.extend({

        initialize: function(options) {
            $.extend(this, options);            
            var self = this;

            this.query = {
                filter:  {
                    terms: ko.observableArray()
                },
                isEmpty: function(){
                    if (this.filter.terms.length === 0){
                        return true;
                    }
                    return false;
                },
                changed: ko.pureComputed(function(){
                    var ret = ko.toJSON(this.query.filter.terms());
                    return ret;
                }, this).extend({ rateLimit: 200 })
            };

        	this.render();
        },

        render: function(){
            var self = this;
            this.searchbox = this.$el.select2({
                multiple: true,
                //maximumselectionsize: 1,
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
                        var value = $('div.resource_search_widget').find('.select2-input').val();
                        //var value = self.searchbox.select2('data');
                        var results = [{
                            inverted: false,
                            type: 'string',
                            context: 'string',
                            id: value,
                            text: value,
                            value: value
                        }];
                        $.each(data.hits.hits, function(){
                            results.push({
                                inverted: false,
                                type: this._source.options.conceptid ? 'concept' : 'term',
                                context: this._source.context,
                                id: this._source.term,
                                text: this._source.term,
                                value: this._source.options.conceptid ? this._source.options.conceptid : this._source.term
                            });
                        }, this);
                        return {results: results};
                    }
                },
                formatResult:function(result, container, query, escapeMarkup){
                    var markup=[];
                    window.Select2.util.markMatch(result.text, query.term, markup, escapeMarkup);
                    var formatedresult = '<span class="concept_result">' + markup.join("")  + '</span><i class="concept_result_schemaname">(' + result.context + ')</i>';
                    //var formatedresult = '<div class="search_term_result" data-id="' + result.id + '"><i class="fa fa-minus" style="margin-right: 7px;display:none;"></i>' + markup.join("") + '</div>';
                    return formatedresult;
                },
                escapeMarkup: function(m) { return m; }
            }).on("select2-selecting", function(e, el) {
                self.trigger("select2-selecting", e, el);
            }).on("change", function(e, el){
                self.trigger("change", e, el);

                if(e.added){
                    self.query.filter.terms.push(e.added);
                }
                if(e.removed){
                    self.query.filter.terms.remove(e.removed);
                }
            });     
        },

        getUrl: function(){
            return arches.urls.search_terms;
        }

    });
});

