define([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'viewmodels/alert',
    'templates/views/components/search/core-search.htm',
], function($, _, ko, arches, AlertViewModel, coreSearchTemplate) {
    const componentName = 'core-search';
    const viewModel = function(params) {
        const self = this;
        this.query = params.query;
        this.queryString = params.queryString;
        this.updateRequest = params.updateRequest;
        this.searchResults = params.searchResults;
        this.userIsReviewer = params.userIsReviewer;
        this.total = params.total;
        this.userid = params.userid;
        this.hits = params.hits;
        this.alert = params.alert;
        let localQueryObj = this.query();
        localQueryObj[componentName] = true;
        this.query(localQueryObj);
        this.queryString.subscribe(function() {
            this.doQuery();
        }, this);

        this.doQuery = function() {
            const queryObj = JSON.parse(this.queryString());

            if (self.updateRequest) {
                self.updateRequest.abort();
            }

            self.updateRequest = $.ajax({
                type: "GET",
                url: arches.urls.search_results,
                data: queryObj,
                context: this,
                success: function(response) {
                    _.each(self.searchResults, function(value, key, results) {
                        if (key !== 'timestamp') {
                            delete self.searchResults[key];
                        }
                    }, this);
                    _.each(response, function(value, key, response) {
                        if (key !== 'timestamp') {
                            self.searchResults[key] = value;
                        }
                    }, this);
                    self.searchResults.timestamp(response.timestamp);
                    self.userIsReviewer(response.reviewer);
                    self.userid(response.userid);
                    self.total(response.total_results);
                    self.hits(response.results.hits.hits.length);
                    self.alert(false);
                },
                error: function(response, status, error) {
                    const alert = new AlertViewModel('ep-alert-red', arches.translations.requestFailed.title, response.responseJSON?.message);
                    if(self.updateRequest.statusText !== 'abort'){
                        self.alert(alert);
                    }
                },
                complete: function(request, status) {
                    self.updateRequest = undefined;
                    window.history.pushState({}, '', '?' + $.param(queryObj).split('+').join('%20'));
                }
            });
        }
    };

    return ko.components.register(componentName, {
        viewModel: viewModel,
        template: coreSearchTemplate,
    });
});
