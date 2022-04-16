define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'select2'
], function($, _, ko, arches) {
    ko.bindingHandlers.termSearch = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var allBindings = allBindingsAccessor();
            var terms = valueAccessor().terms;
            var tags = valueAccessor().tags;

            var notifyValueChange = function(value){
                var val = terms().concat(tags());
                searchbox.select2('data', val); //.trigger('change');
            };

            terms.subscribe(function (value) {
                notifyValueChange(value);
            });

            tags.subscribe(function (value) {
                notifyValueChange(value);
            });

            var searchbox = $(el).select2({
                dropdownCssClass: 'resource_search_widget_dropdown',
                multiple: true,
                minimumInputLength: 2,
                ajax: {
                    url: arches.urls.search_terms,
                    dataType: 'json',
                    data: function(term, page) {
                        return {
                            q: term, // search term
                            page_limit: 30
                        };
                    },
                    results: function(data, page) {
                        var value = $(el).parent().find('.select2-input').val();

                        // this result is being hidden by a style in arches.css
                        // .select2-results li:first-child{
                        //     display:none;
                        // }
                        var results = [];
                        searchbox.groups = [];
                        _.each(data, function(value, searchType) {
                            if (value.length > 0) {
                                searchbox.groups.unshift(searchType);
                            }
                            _.each(value, function(val) {
                                val.inverted = ko.observable(false);
                                results.push(val);
                            }, this);
                        }, this);
                        //res = _.groupBy(results, 'type');
                        var res = [];
                        res.push({
                            inverted: ko.observable(false),
                            type: 'group',
                            context: '',
                            context_label: '',
                            id: '',
                            text: searchbox.groups,
                            value: '',
                            disabled: true
                        });
                        _.each(_.groupBy(results, 'type'), function(value, group){
                            res = res.concat(value);
                        });
                        res.unshift({
                            inverted: ko.observable(false),
                            type: 'string',
                            context: '',
                            context_label: '',
                            id: value,
                            text: value,
                            value: value
                        });
                        return {
                            results: res
                        };
                    }
                },
                id: function(item) {
                    return item.type + item.value + item.context_label;
                },
                formatResult: function(result, container, query, escapeMarkup) {
                    var markup = [];
                    var indent = result.type === 'concept' || result.type === 'term' ? 'term-search-item indent' : (result.type === 'string' ? 'term-search-item' : 'term-search-group');
                    if (result.type === 'group') {
                        _.each(result.text, function(searchType, i) {
                            var label = searchType === 'concepts' ? arches.translations.termSearchConcept : arches.translations.termSearchTerm;
                            var active = i === 0 ? 'active' : '';
                            markup.push('<button id="' + searchType + 'group" class="btn search-type-btn term-search-btn ' + active + ' ">' + label + '</button>');
                        });
                    } else {
                        window.Select2.util.markMatch(result.text, query.term, markup, escapeMarkup);
                    }
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + _.escape(result.context_label) + ')</i>' : '';
                    var formatedresult = '<span class="' + result.type + '"><span class="' + indent + '">' + markup.join("") + '</span>' + context + '</span>';
                    container[0].className = container[0].className + ' ' + result.type;
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
                formatSelection: function(result, container) {
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + _.escape(result.context_label) + ')</i>' : '';
                    var markup = '<span data-filter="external-filter"><i class="fa fa-minus" style="margin-right: 7px;display:none;"></i>' + result.text + '</span>' + context;
                    if (result.inverted()) {
                        markup = '<span data-filter="external-filter"><i class="fa fa-minus inverted" style="margin-right: 7px;"></i>' + result.text + '</span>' + context;
                    }
                    if (result.type !== 'string' && result.type !== 'concept' && result.type !== 'term') {
                        $(container.prevObject).addClass('filter-flag');
                    }
                    return markup;
                },
                escapeMarkup: function(m) {
                    return m;
                }
            }).on('change', function(e, el) {
                if (e.added) {
                    terms.push(e.added);
                }
                if (e.removed) {
                    terms.remove(function(item) {
                        return item.id === e.removed.id && item.context_label === e.removed.context_label;
                    });
                    tags.remove(function(item) {
                        return item.id === e.removed.id && item.context_label === e.removed.context_label;
                    });
                }
            }).on('choice-selected', function(e, el) {
                var selectedTerm = $(el).data('select2-data');
                var terms = searchbox.select2('data');

                if (selectedTerm.id !== "Advanced Search") {
                    if(!selectedTerm.inverted()){
                        $(el).find('.fa-minus').show();
                    }else{
                        $(el).find('.fa-minus').hide();
                    }
                    selectedTerm.inverted(!selectedTerm.inverted());
                }

                //terms(terms);

            }).on('select2-loaded', function(e, el) {
                if (searchbox.groups.length > 0) {
                    if (searchbox.groups[0] === 'concepts'){
                        $('.term').hide();
                    } else {
                        $('.concept').hide();
                    }
                }

            });
            searchbox.select2('data', ko.unwrap(terms).concat(ko.unwrap(tags))).trigger('change');
        }
    };

    return ko.bindingHandlers.termSearch;
});
