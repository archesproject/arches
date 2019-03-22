define([
    'knockout', 'viewmodels/workflow'
], function(ko, Workflow) {
    return ko.components.register('workflow-plugin', {
        viewModel: Workflow,
        template: { require: 'text!templates/views/components/plugins/workflow.htm' }
    });
});
