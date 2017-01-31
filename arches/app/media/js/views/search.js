define([
    'jquery',
    'underscore',
    'knockout',
    'views/search-base-manager'
], function($, _, ko, SearchBaseManagerView) {
    return new SearchBaseManagerView({viewModel:{searchContext:'full-search'}});
});
