require(['jquery', 
    'underscore',
    'backbone',
    'bootstrap',
    'arches', 
    'select2',
    'views/search/term-filter', 
    'views/search/map-filter',
    'views/search/time-filter',
    'views/search/search-results',
    'knockout',
    'plugins/bootstrap-slider/bootstrap-slider.min',
    'views/forms/sections/branch-list',
    'resource-types',
    'bootstrap-datetimepicker',
    'plugins/knockout-select2'], 
    function($, _, Backbone, bootstrap, arches, select2, TermFilter, MapFilter, TimeFilter, SearchResults, ko, Slider, BranchList, resourceTypes) {
    $(document).ready(function() {

        var SearchView = Backbone.View.extend({
            el: $('body'),
            updateRequest: '',

            events: {
                'click #view-saved-searches': 'showSavedSearches',
                'click #clear-search': 'clear',
                'click #map-filter-button': 'toggleMapFilter',
                'click #time-filter-button': 'toggleTimeFilter'
            },

            initialize: function(options) { 
                var self = this;
                var initialcount = $('#search-results-count').data().count;

                this.termFilter = new TermFilter({
                    el: $.find('input.resource_search_widget')[0]
                });

                this.mapFilter = new MapFilter({
                    el: $('#map-filter-container')[0]
                });

                this.timeFilter = new TimeFilter({
                    el: $('#time-filter-container')[0]
                });

                this.searchResults = new SearchResults({
                    el: $('#search-results-container')[0]
                });

                this.searchQuery = {
                    queryString: function(){
                        var params = {
                            page: self.searchResults.page(),
                            termFilter: ko.toJSON(self.termFilter.query.filter.terms()),
                            year_min_max: ko.toJSON(self.timeFilter.query.filter.year_min_max()),
                            temporalFilter: ko.toJSON(self.timeFilter.query.filter.filters()),
                            spatialFilter: ko.toJSON(self.mapFilter.query.filter),
                            mapExpanded: self.mapFilter.expanded(),
                            timeExpanded: self.timeFilter.expanded()
                        }; 
                        return $.param(params);
                    }, 
                    isEmpty: function(){
                        if (self.mapFilter.query.isEmpty() && 
                            self.termFilter.query.isEmpty() && 
                            self.timeFilter.query.isEmpty()){
                            return true;
                        }
                        return false;
                    },
                    changed: ko.pureComputed(function(){
                        var ret = ko.toJSON(this.termFilter.query.changed()) +
                            ko.toJSON(this.timeFilter.query.changed()) +
                            ko.toJSON(this.mapFilter.query.changed());
                        return ret;
                    }, this).extend({ rateLimit: 200 })
                }

                this.getSearchQuery();

                this.searchResults.page.subscribe(function(){
                    console.log('in this.searchResults.page.subscribe');
                    self.doQuery();
                })

                this.searchQuery.changed.subscribe(function(){
                    console.log('in this.searchQuery.changed.subscribe');
                    self.searchResults.page(1);
                    self.doQuery();
                });
            },

            doQuery: function () {
                console.log('in doQuery');
                var self = this;
                var queryString = this.searchQuery.queryString();
                if (this.updateRequest) {
                    this.updateRequest.abort();
                }

                window.history.pushState({}, '', '?'+queryString);

                this.updateRequest = $.ajax({
                    type: "GET",
                    url: arches.urls.search_results,
                    data: queryString,
                    success: function(results){
                        console.log('after success');
                        self.searchResults.updateResults(results);
                        self.toggleSearchResults('show');
                        self.toggleSavedSearches('hide');
                        self.mapFilter.applyBuffer();
                    },
                    error: function(){}
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

            toggleMapFilter: function(){
                if($('#saved-searches').is(":visible")){
                    this.doQuery();
                }
                this.mapFilter.expanded(!this.mapFilter.expanded());
            },

            toggleTimeFilter: function(showOrHide){
                if($('#saved-searches').is(":visible")){
                    this.doQuery();
                }
                this.timeFilter.expanded(!this.timeFilter.expanded());
            },

            slideToggle: function(ele, showOrHide){
                var self = this;
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

            getSearchQuery: function(){
                var doQuery = false;
                var query = _.chain(decodeURIComponent(location.search).slice(1).split('&') )
                    // Split each array item into [key, value]
                    // ignore empty string if search is empty
                    .map(function(item) { if (item) return item.split('='); })
                    // Remove undefined in the case the search is empty
                    .compact()
                    // Turn [key, value] arrays into object parameters
                    .object()
                    // Return the value of the chain operation
                    .value();

                if('page' in query){
                    query.page = JSON.parse(query.page);
                    doQuery = true;
                }
                this.searchResults.restoreState(query.page);


                if('termFilter' in query){
                    query.termFilter = JSON.parse(query.termFilter);
                    doQuery = true;
                }
                this.termFilter.restoreState(query.termFilter);


                if('temporalFilter' in query){
                    query.temporalFilter = JSON.parse(query.temporalFilter);
                    doQuery = true;
                }
                if('year_min_max' in query){
                    query.year_min_max = JSON.parse(query.year_min_max);
                    doQuery = true;
                }
                if('timeExpanded' in query){
                    query.timeExpanded = JSON.parse(query.timeExpanded);
                    doQuery = true;
                }
                this.timeFilter.restoreState(query.temporalFilter, query.year_min_max, query.timeExpanded);


                if('spatialFilter' in query){
                    query.spatialFilter = JSON.parse(query.spatialFilter);
                    doQuery = true;
                }
                if('mapExpanded' in query){
                    query.mapExpanded = JSON.parse(query.mapExpanded);
                    doQuery = true;
                }
                this.mapFilter.restoreState(query.spatialFilter, query.mapExpanded);
                

                if(doQuery){
                    this.doQuery();
                }
                
            },

            clear: function(){
                this.termFilter.clear();
                this.mapFilter.clear();
                this.timeFilter.clear();
            }

        });
        new SearchView();
    });
});