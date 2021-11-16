define([
    'arches',
    'knockout',
], function(arches, ko) {
    function viewModel(params) {
        this.urls = arches.urls;
        this.loading = ko.observable(true);
        this.workflows = ko.observableArray();
        this.resourceid = params.resourceid;
        //We may want to allow a user to navigate to any workflow, so we may want this
        window.fetch(arches.urls.plugin('init-workflow') + '?json=true')
            .then(response => response.json())
            .then(data => this.workflows(data['config']['workflows'].map(function(wf){
                wf.url = '/arches-her' + arches.urls.plugin(wf.slug);
                return wf;
            }, this)));   
    }

    ko.components.register('final-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/final-step.htm'
        }
    });
    return viewModel;
});
