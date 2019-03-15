define([
    'knockout',
], function(ko) {
    var Workflow = function(config) {
        var self = this;
        this.steps = ko.observableArray(config.steps);
        this.activeStepIndex = ko.observable(0);
        this.activeStep = ko.computed(function() {
            var index = self.activeStepIndex;
            return self.steps()[index()];
        });

        this.next = function(){
            if (self.activeStepIndex() < self.steps().length - 1) {
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