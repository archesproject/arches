define([
    'views/components/search/base-filter',
    'knockout',
    'knockout-mapping'],
function(BaseFilter, ko, koMapping) {
    var componentName = 'paging-filter';
    return ko.components.register(componentName, {
        viewModel: BaseFilter.extend({

            events: {
                'click .related-resources-graph': 'showRelatedResouresGraph',
                'click .navigate-map': 'zoomToFeature',
                'mouseover .arches-search-item': 'itemMouseover',
                'mouseout .arches-search-item': 'itemMouseout'
            },

            initialize: function(options) {
                BaseFilter.prototype.initialize.call(this, options);
                this.name = 'Search Results';
                this.page = ko.observable(1);
                this.paginator = koMapping.fromJS({});
                this.showPaginator = ko.observable(false);

                this.page.subscribe(function(timestamp) {
                    this.updateResults(this.searchResults);
                }, this);

                this.filters['search-results'](this);
                this.restoreState();
            },

            newPage: function(page){
                if(page){
                    this.userRequestedNewPage(true);
                    this.page(page);
                }
            },

            restoreState: function(){
                this.page(ko.utils.unwrapObservable(this.query.page));
            },

            updateResults: function(response){
                var self = this;
                koMapping.fromJS(response.paginator, this.paginator);
                this.showPaginator(true);
            }
        }),
        template: { require: 'text!templates/views/components/search/paging-filter.htm' }
    });
});
