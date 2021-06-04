require([
    'jquery',
    'underscore',
    'knockout',
    'arches',
    'views/base-manager',
], function($, _, ko, arches, BaseManagerView) {
    var viewModel = BaseManagerView.extend({
        initialize: function(options){
            var self = this;
            var resourceId = $('#resourceId').data('value');

            this.initialize = function() {
                // if (ko.unwrap(self.resourceid)) {
                    var url = arches.urls.api_resource_report(resourceId);
                    self.fetchResourceData(url);
                // }
                // else {
                    // self.loading(false);
                // }
            };
    
            this.fetchResourceData = function(url) {
                window.fetch(url).then(function(response){
                    if (response.ok) {
                        return response.json();
                    }
                    else {
                        throw new Error(arches.translations.reNetworkReponseError);
                    }
                }).then(function(responseJson) {
                    var template = responseJson.template

                    console.log("D(DS)(D", responseJson)
                    // self.template(template);
        
                    // if (template.preload_resource_data) {
                    //     self.preloadResourceData(responseJson)
                    // }
                    // else {
                    //     self.report(responseJson.resource_instance);
                    // }
        
                    // self.loading(false);

                    self.foo(responseJson.template.componentname)

                    BaseManagerView.prototype.initialize.call(self, options);
                });
            };

            this.foo = ko.observable('bar');

            _.defaults(this.viewModel, {
                showFind: ko.observable(false),
                template: this.foo,
                resourceId: ko.observable(resourceId),
                arches: arches,
            });

            console.log('report vew', self, options)

            this.initialize();
            

            // this.viewModel.resourceId.subscribe(function(graphid) {
            //     if(graphid && graphid !== ""){
            //         console.log("DID)", graphid)
            //         self.viewModel.navigate(arches.urls.add_resource(graphid));
            //     }
            // });

        }
    });

    // var foo = ko.components.register('report', {
    //     viewModel: fooVM,
    //     template: { require: 'text!templates/views/resource/report.htm' }
    // });

    return new viewModel()
});
