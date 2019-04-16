define([
    'knockout',
    'viewmodels/workflow-step'
], function(ko, Step) {
    var Workflow = function(config) {
        var self = this;

        this.steps = config.steps || [];
        this.activeStep = ko.observable();
        this.ready = ko.observable(false);

        this.ready.subscribe(function() {
            self.steps.forEach(function(step, i) {
                if (!(self.steps[i] instanceof Step)) {
                    step.workflow = self;
                    self.steps[i] = new Step(step);
                    self.steps[i].complete.subscribe(function(complete) {
                        if (complete) self.next();
                    });
                }
                self.steps[i]._index = i;
            });
            if (self.steps.length > 0) {
                self.activeStep(self.steps[0]);
            }
        });

        this.next = function(){
            var activeStep = self.activeStep();
            if (activeStep && activeStep.complete() && activeStep._index < self.steps.length - 1) {
                self.activeStep(self.steps[activeStep._index+1]);
            }
        };
        this.back = function(){
            var activeStep = self.activeStep();
            if (activeStep && activeStep._index > 0) {
                self.activeStep(self.steps[activeStep._index-1]);
            }
        };
    };
    return Workflow;
});
