define([
    'jquery',
    'knockout',
    'arches',
    'select2'
], function($, ko, arches) {
    ko.bindingHandlers.termSearch = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var allBindings = allBindingsAccessor();
            var terms = valueAccessor().terms;
            var tags = valueAccessor().tags;

            var notifyValueChange = function(value){
                var val = terms().concat(tags());
                searchbox.select2('data', val)//.trigger('change');
            }

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
                        var results = [{
                            inverted: ko.observable(false),
                            type: 'string',
                            context: '',
                            context_label: '',
                            id: value,
                            text: value,
                            value: value
                        }];
                        $.each(data, function() {
                            this.inverted = ko.observable(false);
                            results.push(this);
                        }, this);
                        return {
                            results: results
                        };
                    }
                },
                formatResult: function(result, container, query, escapeMarkup) {
                    var markup = [];
                    window.Select2.util.markMatch(result.text, query.term, markup, escapeMarkup);
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + result.context_label + ')</i>' : '';
                    var formatedresult = '<span class="concept_result">' + markup.join("") + '</span>' + context;
                    return formatedresult;
                },
                formatSelection: function(result, container) {
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + result.context_label + ')</i>' : '';
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
                
                if(!selectedTerm.inverted()){
                    $(el).find('.fa-minus').show();
                }else{
                    $(el).find('.fa-minus').hide();
                }

                selectedTerm.inverted(!selectedTerm.inverted());
                
                //terms(terms);

            });
            searchbox.select2('data', ko.unwrap(terms).concat(ko.unwrap(tags))).trigger('change');            
        }
    };

    return ko.bindingHandlers.termSearch;
});
