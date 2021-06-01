define([
    'arches',
    'jquery',
    'knockout',
    'knockout-mapping',
], function(arches, $, ko, koMapping) {
    var Foo = function(params) {
        var self = this;

        this.loading = ko.observable(true);

        this.version = arches.version;

        this.resourceid = params.resourceid;
        this.template = ko.observable();
        this.reportData = ko.observable();

        var url = arches.urls.api_resource_report(this.resourceid);

        window.fetch(url)
            .then(function(response){
                if (response.ok) {
                    return response.json();
                }
                else {
                    throw new Error(arches.translations.reNetworkReponseError);
                }
            })
            .then(function(responseJson) {
                self.template(responseJson.template);
                self.reportData(responseJson.resource_instance);

                self.loading(false);
            });

        console.log('foo component', this, params, arches)
    };
    ko.components.register('foo', {
        viewModel: Foo,
        template: { require: 'text!templates/views/components/foo.htm' }
    });
    return Foo;
});
