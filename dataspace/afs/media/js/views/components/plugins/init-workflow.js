define([
    'knockout',
    'arches'
], function(ko, arches) {

    var InitWorkflow = function(params) {
        this.workflows = params.workflows.map(function(wf){
            wf.url = arches.urls.plugin(wf.slug);
            return wf;
        }, this);
    };

    return ko.components.register('init-workflow', {
        viewModel: InitWorkflow,
        template: { require: 'text!templates/views/components/plugins/init-workflow.htm' }
    });
});
