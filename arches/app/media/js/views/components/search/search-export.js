define(['jquery',
    'knockout',
    'arches',
    'bindings/fadeVisible'],
function($, ko, arches) {
    var componentName = 'search-export';
    return ko.components.register(componentName, {
        viewModel: function(params) {
            var self = this;
            this.total = params.total;
            this.query = params.query;
            this.downloadStarted = ko.observable(false);
            this.format = ko.observable('tilecsv');
            this.precision = ko.observable(6);
            this.result = ko.observable();

            this.getSearchParamsFromUrl = function(){
                var urlparams = new window.URLSearchParams(window.location.search);
                var res = {};
                urlparams.forEach(function(v, k){
                    res[k] = v;
                });
                return (res);
            };

            this.url = ko.computed(function() {
                var url = arches.urls.export_results;
                var urlparams = self.getSearchParamsFromUrl();
                var query = self.query();
                urlparams.format = self.format();
                urlparams.precision = self.precision();
                return url + '?' + $.param(urlparams);
            });

            this.getExportData = function(){
                var payload = this.getSearchParamsFromUrl();
                payload.format = this.format();
                payload.precision = this.precision();
                payload.total = this.total();
                $.ajax({
                    type: "GET",
                    url: arches.urls.export_results,
                    data: payload
                }).done(function(response) {
                    self.downloadStarted(true);
                    window.setTimeout(function(){
                        self.downloadStarted(false);
                    }, 9000);
                    self.result(response.message);
                });
            };

            this.executeExport = function(limit){
                if (this.total() > limit) {
                    this.getExportData();
                } else {
                    window.open(this.url());
                }
            };

        },
        template: { require: 'text!templates/views/components/search/search-export.htm'}
    });
});
