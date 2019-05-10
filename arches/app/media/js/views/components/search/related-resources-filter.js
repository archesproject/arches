define(['knockout',
    'views/resource/related-resources-manager',
    'views/components/search/base-filter'
], function(ko, RelatedResourcesManager, BaseFilter) {
    var componentName = 'related-resources-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend ({
            initialize: function(options) {
                options.name = 'Related Resources Filter';
                BaseFilter.prototype.initialize.call(this, options);
                this.ready = ko.observable(false);
                this.options = options;
                // this component is just a light weight wrapper around the relatd resources manager
                // need to wait for the search-resutls filter to be ready
                // before we can load the realated-resources-filter
                // because we need to pass the entire rsearch results filter into the 
                // related resources filter
                var loaded = ko.computed(function(){
                    return this.getFilter('search-results');
                }, this);
                loaded.subscribe(function(loaded) {
                    options.searchResultsVm = this.getFilter('search-results');
                    options.filters[componentName](this);
                    this.ready(true);
                }, this);
            }
        }),
        template: { require: 'text!templates/views/components/search/related-resources-filter.htm'}
    });
});
