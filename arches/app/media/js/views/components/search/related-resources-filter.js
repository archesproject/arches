define(['knockout',
    'views/resource/related-resources-manager',
    'views/components/search/base-filter'
], function(ko, RelatedResourcesManager, BaseFilter) {
    var componentName = 'related-resources-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend ({
            initialize: function(options) {
                options.name = 'Related Resources Filter';
                this.requiredFilters = ['search-results'];
                BaseFilter.prototype.initialize.call(this, options);
                this.ready = ko.observable(false);
                this.options = options;
                // this component is just a light weight wrapper around the relatd resources manager
                // need to wait for the search-resutls filter to be ready
                // before we can load the realated-resources-filter
                // because we need to pass the entire rsearch results filter into the 
                // related resources filter
                if (this.requiredFiltersLoaded() === false) {
                    this.requiredFiltersLoaded.subscribe(function() {
                        options.searchResultsVm = this.getFilter('search-results');
                        options.searchResultsVm.relatedResourcesManager = this;
                        options.filters[componentName](this);
                        this.ready(true);
                    }, this);
                } else {
                    options.searchResultsVm = this.getFilter('search-results');
                    options.searchResultsVm.relatedResourcesManager = this;
                    options.filters[componentName](this);
                    this.ready(true);
                }
            }
        }),
        template: { require: 'text!templates/views/components/search/related-resources-filter.htm'}
    });
});
