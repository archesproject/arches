define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'viewmodels/workflow-step'
], function($, _, ko, koMapping, Step) {
    var Workflow = function(config) {
        var self = this;
        this.steps = config.steps || [];
        this.activeStep = ko.observable();
        this.previousStep = ko.observable();
        this.hoverStep = ko.observable();
        this.ready = ko.observable(false);
        this.loading = config.loading || ko.observable(false);
        this.alert = config.alert || ko.observable(null);
        this.state = {steps:[]};

        this.restoreStateFromURL = function(){
            var urlparams = new window.URLSearchParams(window.location.search);
            var res = {};
            var pathArray = window.location.pathname.split('/');
            res.workflowid = pathArray[2];
            urlparams.forEach(function(v, k){res[k] = v;});
            res.steps = res.steps ? JSON.parse(res.steps) : [];
            this.state = res;
        };

        this.finishWorkflow = function() {
            self.activeStep(self.steps[self.steps.length-1]);
        }

        this.restoreStateFromURL();

        this.ready.subscribe(function() {
            var components = _.unique(self.steps.map(function(step) {return step.component;}));
            require(components, function() {
                // var modules = arguments;
                var stateStepCount = self.state.steps.length;
                self.steps.forEach(function(step, i) {
                    if (!(self.steps[i] instanceof Step)) {
                        step.workflow = self;
                        step.loading = self.loading;
                        step.alert = self.alert;
                        self.steps[i] = new Step(step);
                        if (stateStepCount !== 0 && i <= stateStepCount) {
                            if(self.state.steps[i]) {
                                self.steps[i].complete(self.state.steps[i].complete);
                            }
                        }
                        self.steps[i].complete.subscribe(function(complete) {
                            if (complete) self.next();
                        });
                    }
                    self.steps[i]._index = i;
                });
                if (self.state.activestep) {
                    self.activeStep(self.steps[self.state.activestep]);
                }
                else if(self.steps.length > 0) {
                    self.activeStep(self.steps[0]);
                }
            });
        });

        this.updateUrl = function() {
            //Updates the url with the parameters needed for the next step
            var urlparams = JSON.parse(JSON.stringify(this.state)); //deep copy
            urlparams.steps = JSON.stringify(this.state.steps);
            history.pushState(null, '', window.location.pathname + '?' + $.param(urlparams));
        };

        this.updateState = function(val) {
            //Collects information from the previous step and sets it to the URL
            var activeStep = val;
            var previousStep = self.previousStep();
            var resourceId;
            if (previousStep && previousStep.hasOwnProperty('getStateProperties')) {
                self.state.steps[previousStep._index] = previousStep.getStateProperties();
                self.state.steps[previousStep._index].complete = ko.unwrap(previousStep.complete);
                self.state.activestep = val._index;
                self.state.previousstep = previousStep._index;
                if (!resourceId) {
                    resourceId = !!previousStep.resourceid ? ko.unwrap(previousStep.resourceid) : null;
                    self.state.resourceid = resourceId;
                }
                self.updateUrl();
            }
            self.previousStep(activeStep);
        };

        this.next = function(){
            var activeStep = self.activeStep();
            if (activeStep && activeStep.complete() && activeStep._index < self.steps.length - 1) {
                self.activeStep(self.steps[activeStep._index+1]);
            }
        };

        this.back = function(){
            var activeStep = self.activeStep();
            if (activeStep && activeStep._index > 0) {
                self.activeStep(self.steps[activeStep._index - 1]);
            }
        };
    };
    return Workflow;
});
