define([
    'underscore',
    'jquery',
    'arches',
    'knockout',
    'templates/views/components/workflows/survey-unit-workflow/project-area-overview-step.htm',
    'viewmodels/resource-instance-select',
    'views/components/workflows/survey-unit-workflow/project-area-overview-map',
], function(_, $, arches, ko, ProjectAreaOverviewStepTemplate) {
    function viewModel(params) {
        var self = this;

        console.log("!!!!!!!!!!!")

        this.loading = ko.observable(true);
        this.selectedResourceInstanceId = ko.observable(ko.unwrap(params.form.value) && ko.unwrap(params.form.value)['resourceInstanceId']);

        this.selectedAddresses = ko.observable();
        this.selectedAddresses.subscribe(selectedAddresses => {
            params.form.value({
                resourceInstanceId: self.selectedResourceInstanceId(),
                selectedAddresses: selectedAddresses,
            });
        });

        this.selectedResourceInstance = ko.observable(null);
        this.selectedResourceInstance.subscribe((resourceInstance) => {
            if (resourceInstance) {
                params.form.value({
                    resourceInstanceId: resourceInstance[0]['resourceId']
                });
            }
        });

        this.selectedViewComponent = ko.observable('map');
        this.selectedViewComponent.subscribe(componentString => {
            console.log(componentString)
        });

        this.initialize = () => {
            self.loading(false);
        };

        this.save = () => {
            params.form.complete(true);
        };

        this.initialize();
    }

    ko.components.register('project-area-overview-step', {
        viewModel: viewModel,
        template: ProjectAreaOverviewStepTemplate,
    });
    return viewModel;
});