require(['jquery', 
    'backbone',
    'arches', 
    'views/resource-search', 
    'views/map',
    'openlayers', 
    'knockout'], 
    function($, Backbone, arches, ResourceSearch, MapView, ol, ko) {
    $(document).ready(function() {
        var SearchResultsView = Backbone.View.extend({
            el: $('body'),
            updateRequest: '',

            events: {
                'click .page-button': 'newPage',
                'click #view-saved-searches': 'showSavedSearches'
            },

            initialize: function(options) { 
                var self = this;
                this.searchQuery = {
                    page: ko.observable(),
                    q: ko.observableArray(),
                    queryString: ko.pureComputed(function(){
                        var params = {
                            page: self.searchQuery.page(),
                            q: JSON.stringify(self.searchQuery.q())
                        }; 
                        return $.param(params);
                    })
                }

                this.searchQuery.queryString.subscribe(function(querystring){
                    self.updateResults();
                });

                this.searchbox = new ResourceSearch({
                    el: $.find('input.resource_search_widget')[0]
                });

                this.searchbox.on('change', function(e, el){
                    if(e.added){
                        self.termFilterViewModel.filters.push(e.added);
                    }
                    if(e.removed){
                        self.termFilterViewModel.filters.remove(e.removed);
                    }
                    self.updateTermFilter();
                });

                this.searchRestulsViewModel = {
                    total: ko.observable(),
                    results: ko.observableArray()
                };
                ko.applyBindings(this.searchRestulsViewModel, $('#search-results-list')[0]);
                ko.applyBindings(this.searchRestulsViewModel, $('#search-results-count')[0]);

                this.termFilterViewModel = {
                    filters: ko.observableArray()
                };

                this.getSearchQuery();
            },

            newPage: function(evt){
                var data = $(arguments[0].target).data();
                this.searchQuery.page(data.page);
            },

            updateResults: function () {
                var self = this;
                if (this.updateRequest) {
                    this.updateRequest.abort();
                }
                this.updateRequest = $.ajax({
                    type: "GET",
                    url: arches.urls.search_results,
                    data: this.searchQuery.queryString(),
                    success: function(results){
                        $('#paginator').html(results);
                        self.bind(results);
                        self.toggleSearchResults('show');
                        self.toggleSavedSearches('hide');
                    },
                    error: function(){
                    }
                });
            },

            bind: function(results){
                var self = this;
                var data = $('div[name="search-result-data"]').data();
                
                this.searchRestulsViewModel.total(data.results.hits.total);
                self.searchRestulsViewModel.results.removeAll();
                
                $.each(data.results.hits.hits, function(){
                    self.searchRestulsViewModel.results.push({
                        primaryname: this._source.primaryname,
                        entityid: this._source.entityid,
                        entitytypeid: this._source.entitytypeid,
                        descritption: '',
                        geometries: ko.observableArray(this._source.geometries)
                    });
                });
            },

            showSavedSearches: function(){
                this.toggleSavedSearches('show');
                this.toggleSearchResults('hide');
            },

            hideSavedSearches: function(){
                this.toggleSavedSearches('hide');
                this.toggleSearchResults('show');
            },

            toggleSavedSearches: function(showOrHide){
                var ele = $('#saved-searches');
                this.slideToggle(ele, showOrHide);
            },

            toggleSearchResults: function(showOrHide){
                var ele = $('#search-results');
                this.slideToggle(ele, showOrHide);
            },

            slideToggle: function(ele, showOrHide){
                if ($(ele).is(":visible") && showOrHide === 'hide'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!($(ele).is(":visible")) && showOrHide === 'show'){
                    ele.slideToggle('slow');
                    return;
                }

                if (!showOrHide){
                    ele.slideToggle('slow');                    
                }
            },

            updateTermFilter: function(){
                this.searchQuery.q(this.termFilterViewModel.filters());
            },

            getSearchQuery: function(){
                var query = _.chain( location.search.slice(1).split('&') )
                    // Split each array item into [key, value]
                    // ignore empty string if search is empty
                    .map(function(item) { if (item) return item.split('='); })
                    // Remove undefined in the case the search is empty
                    .compact()
                    // Turn [key, value] arrays into object parameters
                    .object()
                    // Return the value of the chain operation
                    .value();

                if(query.page){
                    this.searchQuery.page(query.page);
                }
                if(query.q){
                    this.searchQuery.q(query.q);
                }

                window.onpopstate = function(event) {
                  //alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
                    //window.location = document.location;
                };
            }


        });

        new SearchResultsView();

    });
});