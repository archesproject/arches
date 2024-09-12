define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'select-woo'
], function($, _, ko, arches) {
    ko.bindingHandlers.termSearch = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var allBindings = allBindingsAccessor();
            var terms = valueAccessor().terms;
            var tags = valueAccessor().tags;
            var language = valueAccessor().language;
            var placeholder = valueAccessor().placeholder;

            tags.subscribe(function(tags) {
                // first clear any existing tags
                searchbox.tags.forEach(tag => {
                    tag.remove();
                });
                searchbox.tags = [];

                tags.forEach(item => {
                    var option = new Option(item.text, item.id, true, true);
                    option.data = item;
                    searchbox.append(option);
                    searchbox.tags.push(option);
                }); 
                searchbox.trigger('change');
                if (ko.unwrap(terms).length == 0 && searchbox.tags.length == 0){
                    searchbox.empty();
                }
            });
            terms.subscribe(function(terms) {
                if (terms.length == 0 && searchbox.tags.length == 0)
                    searchbox.empty();
            });
            var self = this;
            this.stripMarkup = function(m){
                return m.replace(/(<([^>]+)>)/gi, "");
            };

            var searchbox = $(el).selectWoo({
                dropdownCssClass: ':all:',
                placeholder: placeholder,
                multiple: true,
                minimumInputLength: 2,
                data:ko.unwrap(terms).concat(ko.unwrap(tags)),  // initial selection
                ajax: {
                    url: arches.urls.search_terms,
                    dataType: 'json',
                    quietMillis: 500,
                    data: function(requestParams) {
                        let term = requestParams.term || '';
                        return {
                            q: term, // search term
                            lang: language()
                        };
                    },
                    processResults: function(data, params) {
                        window.setTimeout(function() {
                            // handles tabbing into the tags themselves to allow for removal
                            $('.select2-results').on('keydown', (e) => {
                                if (e.keyCode == 9) {
                                    e.preventDefault();
                                    var elem = $('.select2-results button');
                                    elem.focus();
                                }
                            });
                        }, 2000);
                        _.each(data, function(value, searchType) {
                            _.each(value, function(val) {
                                val.inverted = ko.observable(false);
                                val.id = val.type + val.value + val.context_label;
                            }, this);
                        }, this);
                        var res = [];
                        res.push({
                            inverted: ko.observable(false),
                            type: 'string',
                            context: '',
                            context_label: '',
                            id: params.term,
                            text: arches.translations.containsTerm(params.term),
                            value: params.term
                        });
                        if(data.terms.length > 0){
                            res.push({"text": arches.translations.termSearchTerm, "children": data.terms});
                        }
                        if(data.concepts.length > 0){
                            res.push({"text": arches.translations.termSearchConcept, "children": data.concepts});
                        }
                        return {
                            results: res
                        };
                    }
                },
                templateResult: function(result, container) {
                    if (result.loading || result.children) {
                        return result.text;
                    }
                    var markup = [];
                    var indent = result.type === 'concept' || result.type === 'term' ? 'term-search-item indent' : (result.type === 'string' ? 'term-search-item' : 'term-search-group');
                    if (result.type === 'group') {
                        _.each(result.text, function(searchType, i) {
                            var label = searchType === 'concepts' ? arches.translations.termSearchConcept : arches.translations.termSearchTerm;
                            var active = i === 0 ? 'active' : '';
                            markup.push('<button tabindex="0" id="' + searchType + 'group" class="btn search-type-btn term-search-btn ' + active + ' ">' + label + '</button>');
                        });
                    } else {
                        markup.push(self.stripMarkup(result.text));
                        //window.selectWoo.util.markMatch(result.text, query.term, markup, stripMarkup);
                    }
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + _.escape(result.context_label) + ')</i>' : '';
                    var formatedresult = '<span class="' + result.type + '"><span class="' + indent + '">' + markup.join("") + '</span>' + context + '</span>';
                    container.className = container.className + ' ' + result.type;
                    $(container).click(function(event){
                        var btn = event.target.closest('button');
                        if(!!btn && btn.id === 'termsgroup') {
                            $(btn).addClass('active').siblings().removeClass('active');
                            $('.term').show();
                            $('.concept').hide();
                        }
                        if(!!btn && btn.id === 'conceptsgroup') {
                            $(btn).addClass('active').siblings().removeClass('active');
                            $('.concept').show();
                            $('.term').hide();
                        }
                    });
                    return formatedresult;
                },
                templateSelection: function(result, container) {
                    if(result.element.data){
                        result = {
                            ...result,
                            ...result.element.data
                        };
                    }

                    result.text = self.stripMarkup(result.text);

                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + _.escape(result.context_label) + ')</i>' : '';
                    var markup = '<button class="search-tag"><span data-filter="external-filter"><i class="fa fa-minus" style="display:none;"></i>' + result.text + '</span>' + context + '</button>';
                    if (result.inverted()) {
                        markup = '<button class="search-tag"><span data-filter="external-filter"><i class="fa fa-minus"></i>' + result.text + '</span>' + context + '</button>';
                    }
                    if (result.type !== 'string' && result.type !== 'concept' && result.type !== 'term') {
                        $(container).addClass('filter-flag');
                    }else{
                        $(container).addClass('term-flag');
                    }
                    $(container).click(function(event){
                        var btn = event.target.closest('button');
                        if(!!btn && btn.className === 'search-tag') {
                            let params = {el: $(btn), result: result};
                            searchbox.trigger('choice-selected', params);
                        }
                    });
                    $(container).find('span.select2-selection__choice__remove').eq(0)
                        .attr('tabindex', '0').attr('aria-label', 'remove item')
                        .on('keydown', function(evt) {
                            if(evt.keyCode === 13){
                                $(evt.currentTarget).click();
                            }
                        });

                    return markup;
                },
                escapeMarkup: function(m) {
                    return m;
                }
            }).on('select2:select', function(e) {
                terms.push(e.params.data);
            }).on('select2:unselect', function(e) {
                if(e.params.data.element.data){
                    e.params.data = {
                        ...e.params.data,
                        ...e.params.data.element.data
                    };
                }
                terms.remove(function(item) {
                    return item.id === e.params.data.id && item.context_label === e.params.data.context_label;
                });
                tags.remove(function(item) {
                    return item.id === e.params.data.id && item.context_label === e.params.data.context_label;
                });
            }).on('choice-selected', function(e, params) {
                let el = params.el;
                let selectedTerm = params.result;

                if (selectedTerm.id !== "Advanced Search") {
                    if(!selectedTerm.inverted()){
                        $(el).find('.fa-minus').show();
                    }else{
                        $(el).find('.fa-minus').hide();
                    }
                    selectedTerm.inverted(!selectedTerm.inverted());
                }
            });

            searchbox.tags = [];
        }
    };

    return ko.bindingHandlers.termSearch;
});
