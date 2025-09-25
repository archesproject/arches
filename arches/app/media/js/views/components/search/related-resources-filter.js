import ko from 'knockout';
import arches from 'arches';
import RelatedResourcesManager from 'views/resource/related-resources-manager';
import BaseFilter from 'views/components/search/base-filter';
import relatedResourcesFilterTemplate from 'templates/views/components/search/related-resources-filter.htm';
import 'views/components/related-resources-graph';   


var componentName = 'related-resources-filter';
const viewModel = BaseFilter.extend ({
    initialize: function(options) {
        options.name = 'Related Resources Filter';
        BaseFilter.prototype.initialize.call(this, options);
        this.ready = ko.observable(false);
        this.options = options;
        this.urls = arches.urls;
        var self = this;
        var setSearchResults = function(){
            self.searchResultsVm.relatedResourcesManager = self;
            self.ready(true);
        };
        this.searchFilterVms[componentName](this);

        this.searchResultsVm = self.getFilterByType('search-results-type', false);
        if (ko.unwrap(this.searchResultsVm)) {
            this.searchResultsVm = this.searchResultsVm();
            setSearchResults();
        } else {
            this.searchResultsVm.subscribe(searchResultsFilter => {
                if (searchResultsFilter) {
                    this.searchResultsVm = searchResultsFilter;
                    setSearchResults();
                }
            }, this);
        }
    }
});

export default ko.components.register(componentName, {
    viewModel: viewModel,
    template: relatedResourcesFilterTemplate,
});
