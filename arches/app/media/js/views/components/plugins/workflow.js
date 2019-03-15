define([
    'knockout', 'viewmodels/workflow', 'viewmodels/workflow-step'
], function(ko, Workflow, Step) {
    return ko.components.register('workflow-plugin', {
        viewModel: function() {
            this.configJSON = {};
            var steps = [
                new Step({title: 'Step 1'}),
                new Step({title: 'Step 2'}),
                new Step({title: 'Step 3'}),
                new Step({title: 'Step 4'})
            ];
            this.workflow = new Workflow({
                steps: steps
            });
        },
        template: { require: 'text!templates/views/components/plugins/workflow.htm' }
    });
});
