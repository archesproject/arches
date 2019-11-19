define(['jquery',
    'knockout',
    'arches',
    'bindings/fadeVisible'],
function($, ko, arches) {
    var componentName = 'search-export';
    return ko.components.register(componentName, {
        viewModel: function() {
            var self = this;

            this.downloadStarted = ko.observable(false);
            this.format = ko.observable('csv');
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

            this.getExportData = function(){
                var payload = this.getSearchParamsFromUrl();
                payload.format = this.format();
                payload.precision = this.precision();
                $.ajax({
                    type: "GET",
                    url: arches.urls.export_results,
                    data: payload
                }).done(function(response) {
                    self.downloadStarted(true);
                    window.setTimeout(function(){
                        self.downloadStarted(false);
                    }, 9000);
                    self.result(response.length);
                });
            };

        },
        template: { require: 'text!templates/views/components/search/search-export.htm'}
    });
});
