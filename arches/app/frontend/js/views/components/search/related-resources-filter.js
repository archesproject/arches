define(['knockout', 'arches',
    'views/resource/related-resources-manager',
    'views/components/search/base-filter',
    'views/components/related-resources-graph'
], function(ko, arches, RelatedResourcesManager, BaseFilter) {
    var componentName = 'related-resources-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend ({
            initialize: function(options) {
                options.name = 'Related Resources Filter';
                this.requiredFilters = ['search-results'];
                BaseFilter.prototype.initialize.call(this, options);
                this.ready = ko.observable(false);
                this.options = options;
                this.urls = arches.urls;
                var self = this;
                // this component is just a light weight wrapper around the relatd resources manager
                // need to wait for the search-resutls filter to be ready
                // before we can load the realated-resources-filter
                // because we need to pass the entire rsearch results filter into the
                // related resources filter
                var setSearchResults = function(){
                    options.searchResultsVm = self.getFilter('search-results');
                    options.searchResultsVm.relatedResourcesManager = self;
                    options.filters[componentName](self);
                    self.ready(true);
                };

                if (this.requiredFiltersLoaded() === false) {
                    this.requiredFiltersLoaded.subscribe(setSearchResults, this);
                } else {
                    setSearchResults();
                }
            }
        }),
        template: { require: 'text!templates/views/components/search/related-resources-filter.htm'}
    });
});
