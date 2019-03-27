define([
    'knockout',
    'viewmodels/workflow-step'
], function(ko, WorkflowStep) {
    return ko.components.register('new-tile-step', {
        viewModel: function(params) {
            //params.configKeys = ['nodegroup'];
            this.componentname = 'default';
            this.selectedCard = '';
            this.selectedTile = null;
            this.provisionalTileViewModel = null;
            this.reviewer = null;
            this.loading = ko.observable(false);
            //this.form = $data;
            WorkflowStep.apply(this, [params]);
        },
        template: {
            require: 'text!templates/views/components/workflows/new-tile-step.htm'
        }
    });
});
