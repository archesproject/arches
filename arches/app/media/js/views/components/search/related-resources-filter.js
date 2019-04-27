define(['knockout',
    'views/resource/related-resources-manager'
], function(ko, RelatedResourcesManager) {
    return ko.components.register('related-resources-filter', {
        viewModel: function(options) {
            this.ready = ko.observable(false);
            this.options = options;
            // this component is just a light weight wrapper around the relatd resources manager
            // need to wait for the search-resutls filter to be ready
            // before we can load the realated-resources-filter
            // because we need to pass the entire rsearch results filter into the 
            // related resources filter
            var loaded = ko.computed(function(){
                return options.filters['search-results']();
            }, this);
            loaded.subscribe(function(loaded) {
                options.searchResultsVm = options.filters['search-results']();
                options.filters['related-resources-filter'](this);
                this.ready(true);
            }, this);
        },
        template: { require: 'text!templates/views/components/search/related-resources-filter.htm'}
    });
});
