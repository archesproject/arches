define([
    'arches',
    'jquery',
    'knockout',
    'knockout-mapping',
], function(arches, $, ko, koMapping) {
    var Foo = function(params) {
        var self = this;

        this.loading = ko.observable(true);

        this.resourceid = params.resourceid;
        this.template = ko.observable({});
        this.template.subscribe(function(foo) {
            console.log(foo)
        })

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
                self.loading(false);
            });

        console.log('foo component', this, params, )
    };
    ko.components.register('foo', {
        viewModel: Foo,
        template: `
            <div data-bind="if: !$data.loading()">
                <div data-bind='component: $data.template().componentname'
                ></div>
            </div>
        `
    });
    return Foo;
});
