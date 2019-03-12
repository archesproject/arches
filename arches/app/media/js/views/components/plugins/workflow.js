define([
    'knockout',
], function(ko) {
    return ko.components.register('workflow-plugin', {
        viewModel: function() {
            this.configJSON = {};
            var steps = [
                {'color': '#543', 'icon': 'fa-chevron-circle-right'},
                {'color': '#543', 'icon': 'fa-alicorn'},
                {'color': '#543', 'icon': 'fa-air-freshener '},
                {'color': '#543', 'icon': 'fa-android'},
                {'color': '#543', 'icon': 'fa-anchor'},
                {'color': '#543', 'icon': 'fa-alarm-clock'},
                {'color': '#543', 'icon': 'fa-acorn'}
            ];
            this.workflowSteps = ko.observableArray(steps);
        },
        template: { require: 'text!templates/views/components/plugins/workflow.htm' }
    });
});
