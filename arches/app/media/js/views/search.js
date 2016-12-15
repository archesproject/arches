require([
    'jquery',
    'views/search/term-filter', 
    'views/base-manager'
], function($, TermFilter, BaseManagerView) {

    var viewModel = {};

    var termFilter = new TermFilter({
        el: $.find('input.resource_search_widget')[0]
    });
    
    var SearchView = new BaseManagerView({
        viewModel: viewModel
    });

    return SearchView;
});
