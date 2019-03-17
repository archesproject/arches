define([
    'knockout', 'viewmodels/workflow', 'viewmodels/workflow-step'
], function(ko, Workflow, Step) {
    return ko.components.register('workflow-plugin', {
        viewModel: function() {
            this.configJSON = {};
            var steps = [
                new Step({title: 'Step 1', description: 'A description here'}),
                new Step({title: 'Step 2', description: 'A very long and verboser description here that explains many different things about the workflow step'}),
                new Step({title: 'Step 3'}),
                new Step({title: 'Step 4', description: 'Another description here'})
            ];
            this.workflow = new Workflow({
                steps: steps
            });
        },
        template: { require: 'text!templates/views/components/plugins/workflow.htm' }
    });
});
