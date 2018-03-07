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
                }, this)
            };

        	this.render();

            var resize = function() {
                $('.resource_search_widget_dropdown .select2-results').css('maxHeight', $(window).height() - self.$el.offset().top - 100 + 'px');
            };       
            resize();
            $(window).resize(resize);             
        },

        render: function(){
            var self = this;
            this.searchbox = this.$el.select2({
                dropdownCssClass: 'resource_search_widget_dropdown',
                multiple: true,
                minimumInputLength: 2,
                ajax: {
                    url: this.getUrl(),
                    dataType: 'json',
                    data: function (term, page) {
                        return {
                            q: term, // search term
                            group_root_node: self.termFilterGroup || 'No group',
                            page_limit: 30
                        };
                    },
                    results: function (data, page) {
                        var value = $('div.resource_search_widget'+this.index).find('.select2-input').val();
                        if (!value) {
                            value = $('div.resource_search_widget').find('.select2-input').val();
                        }
                        // this result is being hidden by a style in arches.css 
                        // .select2-results li:first-child{
                        //     display:none;
                        // } 
                        var results = [{
                            inverted: false,
                            type: 'string',
                            context: '',
                            context_label: '',
                            id: value,
                            text: value,
                            value: value
                        }];
                        $.each(data.hits.hits, function(){
                            results.push({
                                inverted: false,
                                type: this._source.options.conceptid ? 'concept' : 'term',
                                context: this._source.context,
                                context_label: this._source.options.context_label,
                                id: this._source.term + this._source.context,
                                text: this._source.term,
                                value: this._source.options.conceptid ? this._source.options.conceptid : this._source.term
                            });
                        }, this);
                        return {results: results};
                    }.bind(this)
                },
                formatResult:function(result, container, query, escapeMarkup){
                    var markup=[];
                    window.Select2.util.markMatch(result.text, query.term, markup, escapeMarkup);
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + result.context_label + ')</i>' : '';
                    var formatedresult = '<span class="concept_result">' + markup.join("")  + '</span>' + context;
                    return formatedresult;
                },
                formatSelection: function(result){
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + result.context_label + ')</i>' : '';
                    var markup = '<span data-filter="external-filter"><i class="fa fa-minus" style="margin-right: 7px;display:none;"></i>' + result.text + '</span>' + context;
                    if(result.inverted){
                        markup = '<span data-filter="external-filter"><i class="fa fa-minus inverted" style="margin-right: 7px;"></i>' + result.text + '</span>' + context;
                    }
                    return markup;
                },
                escapeMarkup: function(m) { return m; }
            }).on('select2-selecting', function(e, el) {
                self.trigger('select2-selecting', e, el);
            }).on('change', function(e, el){
                self.trigger('change', e, el);

                if(e.added){
                    if(e.added.type !== 'filter-flag'){
                        self.query.filter.terms.push(e.added);                        
                    }

                }
                if(e.removed){
                    if(e.removed.type === 'filter-flag'){
                        self.trigger('filter-removed', e.removed);
                    }else{
                        self.query.filter.terms.remove(function(item){
                            return item.id === e.removed.id && item.context_label === e.removed.context_label;
                        });                   
                    }
                }
            }).on('choice-selected', function(e, el) {
                var data = $(el).data('select2-data');
                self.trigger('choice-selected', e, el);

                if ($(el).hasClass('inverted')) {
                    $(el).removeClass('inverted');
                    $(el).find('.fa-minus').hide();
                } else {
                    $(el).addClass('inverted');
                    $(el).find('.fa-minus').show();
                }
                if (data.inverted != $(el).hasClass('inverted')) {
                    data.inverted = $(el).hasClass('inverted');
                    self.trigger('change');
                }

                // filter-flag types don't rebuild the array and hence don't trigger a an updated search
                // instead they listen to choice-selected events and use that
                if (data.type == 'string' || data.type == 'concept' || data.type == 'term') {
                    self.query.filter.terms.removeAll();
                    $.each(self.searchbox.select2('data'), function(index, term){
                        self.query.filter.terms.push(term);
                    });
                }
                if (data.type == 'filter-flag'){
                    self.trigger('filter-inverted', data);
                }
            });    
        },

        getUrl: function(){
            return arches.urls.search_terms;
        },

        addTag: function(term, inverted){
            var terms = this.searchbox.select2('data');
            terms.unshift({
                inverted: inverted,
                type: 'filter-flag',
                context: '',
                context_label: '',
                id: term,
                text: term,
                value: term
            });

            this.updateTerms(terms);
        },

        removeTag: function(term){
            var terms = this.searchbox.select2('data');
            for (var i=terms.length-1; i>=0; i--) {
                if(terms[i].id == term && terms[i].text == term && terms[i].value == term){
                    terms.splice(i, 1);
                    break;
                }
            }

            this.updateTerms(terms);
        },

        updateTerms: function(terms){
            this.searchbox.select2('data', terms);

            $('.resource_search_widget'+this.index).find('.select2-search-choice').each(function(i, el) {
                if ($(el).data('select2-data').type === 'filter-flag') {
                    $(el).addClass('filter-flag');
                }
                if ($(el).data('select2-data').inverted) {
                    $(el).addClass('inverted');
                }
            });
        },

        restoreState: function(filter){
            var self = this;
            if(typeof filter !== 'undefined' && filter.length > 0){
                var results = [];
                $.each(filter, function(){
                    self.query.filter.terms.push(this);

                    results.push({
                        inverted: this.inverted,
                        type: this.type,
                        context: this.context,
                        context_label: this.context_label,
                        id: this.id,
                        text: this.text,
                        value: this.value
                    });
                });

                this.searchbox.select2('data', results).trigger('change');

                $('.resource_search_widget'+this.index).find('.select2-search-choice').each(function(i, el) {
                    if ($(el).data('select2-data').inverted) {
                        $(el).addClass('inverted');
                    }
                });
            }
        },

        clear: function(){
            this.query.filter.terms.removeAll();
            this.searchbox.select2('data', []);
        }

    });
});

