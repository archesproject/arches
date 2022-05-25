define([
    'jquery',
    'knockout',
    'arches',
], function($, ko, arches) {
    function viewModel(params) {
        var self = this;
        this.digitalResourceGraphId = '707cbd78-ca7a-11e9-990b-a4d18cec433a';
        this.physicalThingResourceId = ko.observable();
        this.relatedDigitalResources = ko.observableArray();

        this.dataLoaded = ko.observable(false);

        const getDigitalResources = async function(resourceid) {
            const url = `${arches.urls.root}digital-resources-by-object-parts/${resourceid}`;
            const result = await fetch(url, {
                method: 'GET',
                credentials: 'include'
            });
            if (result.ok) {
                const results = await result.json();
                const resources = results.resources;

                resources.forEach(function(resource) {
                    resource.selected = ko.observable(false);
                    if(params.value()) {
                        params.value().digitalResources.forEach(function(val) {
                            if (val.resourceid === resource.resourceid) {
                                resource.selected(val.selected);
                            }
                        });
                    }
                });
                self.relatedDigitalResources(resources);
                self.dataLoaded(true);
            }
        };

        this.selectedDigtalResources = ko.pureComputed(function() {
            return self.relatedDigitalResources().map(function(resource){
                return {
                    resourceid: resource.resourceid,
                    partresourceid: resource.partresourceid,
                    selected: resource.selected()
                };
            });
        });

        this.selectedDigtalResources.subscribe(function(val) {
            const data = {digitalResources: val, resourceid: self.physicalThingResourceId()};
            params.value(data);
        });

        this.physicalThingResourceId.subscribe(getDigitalResources);

        if (params.value()) {
            self.physicalThingResourceId(params.value().resourceid);
            getDigitalResources(params.value().resourceid);
        }
    }

    ko.components.register('select-dataset', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/workflows/review-dataset/select-dataset.htm' }
    });
    return viewModel;
});
