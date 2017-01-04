define([
    'jquery',
    'knockout',
    'arches',
    'select2'
], function($, ko, arches) {
    ko.bindingHandlers.termSearch = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var self = this;
            var selection = valueAccessor();

            selection.subscribe(function (value) {
                searchbox.select2('data', value).trigger('change');
                $(el).parent().find('.select2-search-choice').each(function(i, el) {
                    if ($(el).data('select2-data').inverted) {
                        $(el).addClass('inverted');
                    }
                });
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
                            inverted: false,
                            type: 'string',
                            context: '',
                            context_label: '',
                            id: value,
                            text: value,
                            value: value
                        }];
                        $.each(data.hits.hits, function() {
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
                formatSelection: function(result) {
                    var context = result.context_label != '' ? '<i class="concept_result_schemaname">(' + result.context_label + ')</i>' : '';
                    var markup = '<span data-filter="external-filter"><i class="fa fa-minus" style="margin-right: 7px;display:none;"></i>' + result.text + '</span>' + context;
                    if (result.inverted) {
                        markup = '<span data-filter="external-filter"><i class="fa fa-minus inverted" style="margin-right: 7px;"></i>' + result.text + '</span>' + context;
                    }
                    return markup;
                },
                escapeMarkup: function(m) {
                    return m;
                }
            }).on('change', function(e, el) {
                if (e.added) {
                    selection.push(e.added);
                }
                if (e.removed) {
                    selection.remove(function(item) {
                        return item.id === e.removed.id && item.context_label === e.removed.context_label;
                    });
                }
            }).on('choice-selected', function(e, el) {
                var data = $(el).data('select2-data');

                if ($(el).hasClass('inverted')) {
                    $(el).removeClass('inverted');
                    $(el).find('.fa-minus').hide();
                } else {
                    $(el).addClass('inverted');
                    $(el).find('.fa-minus').show();
                }
                data.inverted = $(el).hasClass('inverted');

                selection.removeAll();
                $.each(searchbox.select2('data'), function(index, term) {
                    selection.push(term);
                });
            });
            searchbox.select2('data', ko.unwrap(selection)).trigger('change');
        }
    };

    return ko.bindingHandlers.termSearch;
});
