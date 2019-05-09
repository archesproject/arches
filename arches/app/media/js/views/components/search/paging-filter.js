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
                options.name = 'Paging Filter';
                BaseFilter.prototype.initialize.call(this, options);
                this.page = ko.observable();
                this.paginator = koMapping.fromJS({
                    current_page: 1,
                    end_index: 1,
                    has_next: false,
                    has_other_pages: true,
                    has_previous: false,
                    next_page_number: 2,
                    pages: [],
                    previous_page_number: null,
                    start_index: 1
                });
                //this.showPaginator = ko.observable(true);
                this.userRequestedNewPage = ko.observable(false);

                this.page.subscribe(function(timestamp) {
                    this.updateQuery();
                }, this);

                this.searchResults.timestamp.subscribe(function(timestamp) {
                    this.updateResults();
                }, this);

                this.filters[componentName](this);
                this.restoreState();
            },

            updateQuery: function() {
                var queryObj = this.query();
                queryObj[componentName] = this.page();
                this.query(queryObj);

                // var self = this;
                // koMapping.fromJS(this.searchResults.paginator, this.paginator);
                // this.showPaginator(true);
            },

            newPage: function(page){
                if(page){
                    this.userRequestedNewPage(true);
                    this.page(page);
                }
            },

            restoreState: function(){
                var currentPage = this.query()[componentName];
                if (!currentPage) {
                    currentPage = 1;
                }
                this.page(currentPage);
                this.updateResults();
            },

            updateResults: function() {
                if(!!this.searchResults[componentName] && !!this.searchResults[componentName]['paginator']) {
                    koMapping.fromJS(this.searchResults[componentName]['paginator'], this.paginator);
                }
                //this.showPaginator(true);
            }
        }),
        template: { require: 'text!templates/views/components/search/paging-filter.htm' }
    });
});
