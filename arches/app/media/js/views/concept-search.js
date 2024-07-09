define(['jquery', 'underscore', 'backbone', 'select-woo', 'arches'], function($, _, Backbone, Select2, arches) {
    return Backbone.View.extend({

        initialize: function(options) {
            $.extend(this, options);
            this.render();
        },

        render: function(){
            var self = this;
            this.searchbox = this.$el.find('select.concept_search_widget').selectWoo({
                multiple: false,
                maximumselectionsize: 1,
                minimumInputLength: 2,
                placeholder: arches.translations.searchForAConcept,
                ajax: {
                    url: this.getUrl,
                    dataType: 'json',
                    data: function(requestParams) {
                        let term = requestParams.term || '';
                        let page = requestParams.page || 1;
                        return {
                            q: term, // search term
                            page_limit: 30
                        };
                    },
                    processResults: function(data) {
                        var results = [];
                        $.each(data.hits.hits, function(){
                            results.push({
                                id: this._source.conceptid,
                                text: this._source.value,
                                scheme_id: this._type,
                                scheme: this.in_scheme_name
                            });
                        }, this);
                        return {
                            "results": results,
                            "pagination": {
                                "more": false
                            }
                        };
                    }
                },
                templateResult:function(result){
                    result.scheme = result.scheme ? '(' + _.escape(result.scheme) + ')' : '';
                    var formatedresult = $('<span class="concept_result">' + result.text  + '</span><i class="concept_result_schemaname">' + result.scheme + '</i>');
                    return formatedresult;
                },
                escapeMarkup: function(m) { return m; }
            }).on("select2:selecting", function(e) {
                self.trigger("select2:selecting", e);
            }); 
        },

        getUrl: function(){
            return arches.urls.concept_search;
        }

    });
});