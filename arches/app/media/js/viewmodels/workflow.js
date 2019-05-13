define([
    'jquery',
    'knockout',
    'viewmodels/workflow-step'
], function($, ko, Step) {
    var Workflow = function(config) {
        var self = this;
        var urlParams = new window.URLSearchParams(window.location.search);
        var initstep = Number(urlParams.get('step')) || undefined;
        this.steps = config.steps || [];
        this.activeStep = ko.observable();
        this.ready = ko.observable(false);
        this.loading = config.loading || ko.observable(false);
        this.alert = config.alert || ko.observable(null);

        this.ready.subscribe(function() {
            self.steps.forEach(function(step, i) {
                if (!(self.steps[i] instanceof Step)) {
                    step.workflow = self;
                    step.loading = self.loading;
                    step.alert = self.alert;
                    self.steps[i] = new Step(step);
                    self.steps[i].complete.subscribe(function(complete) {
                        if (complete) self.next();
                    });
                }
                self.steps[i]._index = i;
            });
            if (initstep) {
                self.activeStep(self.steps[initstep - 1]);
            }
            else if(self.steps.length > 0) {
                self.activeStep(self.steps[0]);
            }
        });

        this.updateUrl = function(step, direction) {
            //Updates the url with the parameters needed for the next step
            var urlparams;
            if (direction === 'forward') {
                urlparams = step.getForwardUrlParams();
                urlparams.step = step._index + 2;
            } else if (direction === 'backward') {
                urlparams = step.getBackwardUrlParams();
                urlparams.step = step._index;
            }
            history.pushState(null, '', window.location.pathname + '?' + $.param(urlparams));
        };

        this.next = function(){
            var activeStep = self.activeStep();
            self.updateUrl(activeStep, 'forward');
            if (activeStep && activeStep.complete() && activeStep._index < self.steps.length - 1) {
                self.activeStep(self.steps[activeStep._index+1]);
            }
        };

        this.back = function(){
            var activeStep = self.activeStep();
            self.updateUrl(activeStep, 'backward');
            if (activeStep && activeStep._index > 0) {
                self.activeStep(self.steps[activeStep._index-1]);
            }
        };
    };
    return Workflow;
});
