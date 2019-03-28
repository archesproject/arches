define([
    'knockout',
    'viewmodels/workflow-step', 
    // 'views/components/workflows/new-tile-step'
], function(ko, Step, NewTileStep) {
    var Workflow = function(config) {
        var self = this;
        this.steps = ko.observableArray([
            new Step({title: 'Step 1', description: 'A description here', component: 'new-tile-step'}),
            new Step({title: 'Step 2', description: 'A very long and verboser description here that explains many different things about the workflow step'}),
            new Step({title: 'Step 3'}),
            new Step({title: 'Step 4', description: 'Another description here'})
        ]);
        this.activeStepIndex = ko.observable(0);
        this.activeStep = ko.computed(function() {
            this.steps().forEach(function(step){
                step.active(false);
            });
            var activeStep = self.steps()[self.activeStepIndex()];
            activeStep.active(true);
            return activeStep;
        }, this);

        this.next = function(){
            if (self.activeStepIndex() < self.steps().length - 1) {
                this.activeStep().complete(true);
                self.activeStepIndex(self.activeStepIndex() + 1);
            }
        };
        this.back = function(){
            if (self.activeStepIndex() > 0) {
                self.activeStepIndex(self.activeStepIndex() - 1);
            }
        };
    };
    return Workflow;
});