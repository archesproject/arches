import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import koMapping from 'knockout-mapping';
import SearchComponents from 'search-components';
import BaseManagerView from 'views/base-manager';
import ariaUtils from 'utils/aria';
import DatatypeConfigComponents from 'datatype-config-components';


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
    this.searchFilterVms = {};
    this.searchFilterConfigs = Object.values(SearchComponents);
    this.defaultSearchViewConfig = this.searchFilterConfigs.find(filter => filter.type == "search-view");
    this.searchViewComponentName = ko.observable(false);
    this.getFilter = function(filterName, unwrap=true) {
        if (unwrap)
            return ko.unwrap(this.searchFilterVms[filterName]);
        return this.searchFilterVms[filterName];
    };
    this.getFilterByType = function(type, unwrap=true) {
        const filter = this.searchFilterConfigs.find(component => component.type == type);
        if (!filter)
            return null;
        if (unwrap)
            return ko.unwrap(this.searchFilterVms[filter.componentname]);
        return this.searchFilterVms[filter.componentname];
    };
    Object.values(SearchComponents).forEach(function(component) {
        this.searchFilterVms[component.componentname] = ko.observable(null);
        // uncomment below to test for any filters that don't load as expected
        // this.searchFilterVms[component.componentname].subscribe(vm => {console.log(component.componentname+" loaded");})
    }, this);
    this.searchViewFiltersLoaded = ko.computed(function() {
        let res = true;
        Object.entries(this.searchFilterVms).forEach(function([componentName, filter]) {
            res = res && ko.unwrap(filter);
        });
        return res;
    }, this);
    this.query = ko.observable(getQueryObject());
    if (this.query()["search-view"] !== undefined) {
        this.searchViewComponentName(this.query()["search-view"]);
    } else {
        this.searchViewComponentName(this.defaultSearchViewConfig.componentname);
    }
    this.queryString = ko.computed(function() {
        return JSON.stringify(this.query());
    }, this);
    this.mouseoverInstanceId = ko.observable();
    this.mapLinkData = ko.observable(null);
    this.userIsReviewer = ko.observable(null);
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

export default new SearchView();
