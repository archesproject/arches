define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'search-components',
    'views/base-manager',
    'utils/aria',
    'datatype-config-components'
], function($, _, ko, koMapping, SearchComponents, BaseManagerView, ariaUtils) {
    // a method to track the old and new values of a subscribable
    // from https://github.com/knockout/knockout/issues/914
    //
    // use case:
    // var sub1 = this.FirstName.subscribeChanged(function (newValue, oldValue) {
    //     this.NewValue1(newValue);
    //     this.OldValue1(oldValue);
    // }, this);

    ko.subscribable.fn.subscribeChanged = function(callback, context) {
        var savedValue = this.peek();
        return this.subscribe(function(latestValue) {
            var oldValue = savedValue;
            savedValue = latestValue;
            callback.call(context, latestValue, oldValue);
        });
    };

    var getQueryObject = function() {
        var query = _.chain(decodeURIComponent(location.search).slice(1).split('&'))
            // Split each array item into [key, value]
            // ignore empty string if search is empty
            .map(function(item) {
                if (item) return item.split('=');
            })
            // Remove undefined in the case the search is empty
            .compact()
            // Turn [key, value] arrays into object parameters
            .object()
            // Return the value of the chain operation
            .value();
        return query;
    };

    var CommonSearchViewModel = function() {
        this.filters = {};
        this.filtersList = _.sortBy(Object.values(SearchComponents), function(filter) {
            return filter.sortorder;
        }, this);
        Object.values(SearchComponents).forEach(function(component) {
            this.filters[component.componentname] = ko.observable(null);
        }, this);
        this.query = ko.observable(getQueryObject());
        this.queryString = ko.computed(function() {
            return JSON.stringify(this.query());
        }, this);
        this.mouseoverInstanceId = ko.observable();
        this.mapLinkData = ko.observable(null);
        this.userIsReviewer = ko.observable(false);
        this.userid = ko.observable(null);
        this.searchResults = {'timestamp': ko.observable()};
    };
    
    var SearchView = BaseManagerView.extend({
        initialize: function(options) {
            this.viewModel.sharedStateObject = new CommonSearchViewModel();
            this.viewModel.total = ko.observable();
            this.viewModel.hits = ko.observable();
            _.extend(this, this.viewModel.sharedStateObject);
            this.viewModel.sharedStateObject.total = this.viewModel.total;
            this.viewModel.sharedStateObject.hits = this.viewModel.hits;
            this.viewModel.sharedStateObject.alert = this.viewModel.alert;
            this.viewModel.sharedStateObject.loading = this.viewModel.loading;
            this.viewModel.sharedStateObject.resources = this.viewModel.resources;
            this.viewModel.sharedStateObject.userCanEditResources = this.viewModel.userCanEditResources;
            this.viewModel.sharedStateObject.userCanReadResources = this.viewModel.userCanReadResources;
            this.shiftFocus = ariaUtils.shiftFocus;
            this.viewModel.loading(true);

            BaseManagerView.prototype.initialize.call(this, options);
            this.viewModel.sharedStateObject.menuActive = this.viewModel.menuActive;
        },
    });

    return new SearchView();
});
