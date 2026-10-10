import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import Backbone from 'backbone';
import arches from 'arches';
import AlertViewModel from 'viewmodels/alert';


export default Backbone.View.extend({
    constructor: function() {
        this.name = 'Base Search View';
        this.filter = {};
        this.defaultQuery = {};
        Backbone.View.apply(this, arguments);
    },

    initialize: function(sharedStateObject) {
        const self = this;
        $.extend(this, sharedStateObject);
        this.query = sharedStateObject.query;
        this.queryString = sharedStateObject.queryString;
        this.updateRequest = sharedStateObject.updateRequest;
        this.userIsReviewer = sharedStateObject.userIsReviewer;
        this.total = sharedStateObject.total;
        this.userid = sharedStateObject.userid;
        this.hits = sharedStateObject.hits;
        this.alert = sharedStateObject.alert;
        this.sharedStateObject = sharedStateObject;
        this.queryString.subscribe(function() {
            if (this.searchViewFiltersLoaded()) {
                this.doQuery();
            } else {
                this.searchViewFiltersLoaded.subscribe(function() {
                    this.doQuery();
                }, this);
            }
        }, this);
        // init query
        if (self.updateRequest === undefined) {
            if (this.searchViewFiltersLoaded()) {
                this.doQuery();
            } else {
                this.searchViewFiltersLoaded.subscribe(function() {
                    this.doQuery();
                }, this);
            }
        }
    },

    doQuery: function() {
        const queryObj = JSON.parse(this.queryString());
        if (this.updateRequest) { this.updateRequest.abort(); }
        const request = this.updateRequest = $.ajax({
            type: "GET",
            url: arches.urls.search_results,
            data: queryObj,
            context: this,
            success: function(response) {
                _.each(this.sharedStateObject.searchResults, function(value, key, results) {
                    if (key !== 'timestamp') {
                        delete this.sharedStateObject.searchResults[key];
                    }
                }, this);
                _.each(response, function(value, key, response) {
                    if (key !== 'timestamp') {
                        this.sharedStateObject.searchResults[key] = value;
                    }
                }, this);
                this.sharedStateObject.searchResults.timestamp(response.timestamp);
                this.sharedStateObject.userIsReviewer(response.reviewer);
                this.sharedStateObject.userid(response.userid);
                this.sharedStateObject.total(response.total_results);
                this.sharedStateObject.hits(response.results.hits.hits.length);
                this.sharedStateObject.alert(false);

                // only record history for completed queries, and skip duplicates
                const newSearch = '?' + $.param(queryObj).split('+').join('%20');
                if (newSearch !== window.location.search) {
                    window.history.pushState({}, '', newSearch);
                }
            },
            error: function(response, status, error) {
                const alert = new AlertViewModel('ep-alert-red', arches.translations.requestFailed.title, response.responseJSON?.message);
                if(status !== 'abort'){
                    this.alert(alert);
                }
                this.sharedStateObject.loading(false);
            },
            complete: function() {
                if (this.updateRequest === request) { this.updateRequest = undefined; }
                this.sharedStateObject.loading(false);
            }
        });
    },

    clearQuery: function(){
        Object.values(this.searchFilterVms).forEach(function(value){
            if (value()){
                if (value().clear){
                    value().clear();
                }
            }
        }, this);
        this.query(this.defaultQuery);
    },
});
