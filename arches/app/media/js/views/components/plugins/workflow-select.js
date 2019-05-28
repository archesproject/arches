define([
    'knockout', 'viewmodels/workflow-select'
], function(ko, WorkflowSelect) {
    return ko.components.register('workflow-select-plugin', {
        viewModel: WorkflowSelect,
        template: { require: 'text!templates/views/components/plugins/workflow-select.htm' }
    });
});