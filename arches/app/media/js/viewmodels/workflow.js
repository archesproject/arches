define([
    'arches',
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'viewmodels/alert',
    'viewmodels/workflow-step'
], function(arches, $, _, ko, koMapping, uuid, AlertViewModel, Step) {
    WORKFLOW_ID_LABEL = 'workflow-id';
    STEP_ID_LABEL = 'workflow-step-id';

    var Workflow = function(config) {
        var self = this;

        this.id = ko.observable();  
        
        this.steps = config.steps || [];
        this.stepIds = ko.observableArray();
        
        this.hoverStep = ko.observable();
        this.previousStep = ko.observable();

        this.activeStep = ko.observable();
        this.activeStep.subscribe(function() {
            self.checkCanFinish();
        });

        this.ready = ko.observable(false);
<<<<<<< HEAD
        this.ready.subscribe(function() {
            var components = _.unique(self.steps.map(function(step) {return step.component;}));
            require(components, function() { self.initialize(); });
        });

=======
        this.tabbedWorkflow = ko.observable(ko.unwrap(config.tabbedWorkflow));
>>>>>>> 5167f1ff625d855ae1950d6236b6337aecaba660
        this.loading = config.loading || ko.observable(false);

        this.workflowName = ko.observable();
        this.canFinish = ko.observable(false);
        this.alert = config.alert || ko.observable(null);
        this.state = {steps:[]};
        this.quitUrl = arches.urls.home;
        this.wastebinWarning = function(val){
            return [[arches.translations.workflowWastbinWarning.replace("${val}", val)],[arches.translations.workflowWastbinWarning2]];
        };
        this.warning = '';

        this.initialize = function() {
            var cachedWorkflowId = self.getWorkflowIdFromUrl();
            if (cachedWorkflowId && self.getStepIdsFromLocalStorage(cachedWorkflowId)) {
                self.id(cachedWorkflowId)
            }
            else {
                self.id(uuid.generate());
                self.setWorkflowIdToUrl();
            }
            
            self.createSteps();

            var cachedActiveStep = self.steps.find(function(step) {
                return step.id() === self.getStepIdFromUrl();
            });

            if (cachedActiveStep) {
                self.activeStep(cachedActiveStep);
            }
            else {
                self.removeStepIdFromUrl();

                if (self.state.activestep) {
                    self.activeStep(self.steps[self.state.activestep]);
                }
                else if(self.steps.length > 0) {
                    self.activeStep(self.steps[0]);
                }
            }
        };

        this.createSteps = function() {
            var stateStepCount = self.state.steps.length;
            var generatedStepIds = [];

            var cachedStepIds = self.getStepIdsFromLocalStorage(self.id());

            self.steps.forEach(function(step, i) {
                if (!(self.steps[i] instanceof Step)) {
                    step.workflow = self;
                    step.loading = self.loading;
                    step.alert = self.alert;

                    /* if stepIds exist for this workflow in localStorage, set correct value */ 
                    if (cachedStepIds) { step.id = cachedStepIds[i]; }

                    var newStep = new Step(step);
                    self.steps[i] = newStep;

                    /* if stepIds DO NOT exist for this workflow in localStorage, add id to accumulator */ 
                    if (!cachedStepIds) { generatedStepIds.push(newStep.id()); }

                    if (stateStepCount !== 0 && i <= stateStepCount) {
                        if(self.state.steps[i]) {
                            self.steps[i].complete(self.state.steps[i].complete);
                        }
                    }
                    self.steps[i].complete.subscribe(function(complete) {
                        if (complete && self.steps[i].autoAdvance()) self.next();
                    });
                }
                self.steps[i]._index = i;
            });

            /* if stepIds DO NOT exist for this workflow in localStorage, set them */ 
            if (!cachedStepIds) { self.setStepIdsToLocalStorage(generatedStepIds); }
        };

        this.getStepIdFromUrl = function() {
            var searchParams = new URLSearchParams(window.location.search);
            return searchParams.get(STEP_ID_LABEL);
        };

        this.removeStepIdFromUrl = function() {
            var searchParams = new URLSearchParams(window.location.search);
            searchParams.delete(STEP_ID_LABEL);

            var newRelativePathQuery = `${window.location.pathname}?${searchParams.toString()}`;
            history.replaceState(null, '', newRelativePathQuery);
        };

        this.getWorkflowIdFromUrl = function() {
            var searchParams = new URLSearchParams(window.location.search);
            return searchParams.get(WORKFLOW_ID_LABEL);
        };
        
        this.setWorkflowIdToUrl = function() {
            var searchParams = new URLSearchParams(window.location.search);
            searchParams.set(WORKFLOW_ID_LABEL, self.id());

            var newRelativePathQuery = `${window.location.pathname}?${searchParams.toString()}`;
            history.replaceState(null, '', newRelativePathQuery);
        };

        this.getStepIdsFromLocalStorage = function(workflowId) {
            return JSON.parse(localStorage.getItem(`${WORKFLOW_ID_LABEL}-${workflowId}`));
        };

        this.setStepIdsToLocalStorage = function(stepIds) {
            return localStorage.setItem(`${WORKFLOW_ID_LABEL}-${self.id()}`, JSON.stringify(stepIds));
        };

        this.getJSON = function(pluginJsonFileName) {
            $.ajax({
                type: "GET",
                url: arches.urls.plugin(pluginJsonFileName),
                data: { "json":true },
                context: self,
                success: function(workflowJson){ self.workflowName(workflowJson.name); }
            });
        };

        this.checkCanFinish = function(){
            var required = false, canFinish = true, complete = null;
            for(var i = 0; i < self.steps.length; i++) {
                required = ko.unwrap(self.steps[i].required);
                complete = ko.unwrap(self.steps[i].complete);
                if(!complete && required) {
                    canFinish = false;
                    break;
                }
            }
            self.canFinish(canFinish);
        };

        this.finishWorkflow = function() {
            if(self.canFinish()){ self.activeStep(self.steps[self.steps.length-1]); }
        };

        this.quitWorkflow = function(){
            var resourcesToDelete = [];
            var tilesToDelete = [];
            var warnings = []
            self.state.steps.forEach(function(step) {
                if (step.wastebin && step.wastebin.resourceid) {
                    warnings.push(step.wastebin.description);
                    resourcesToDelete.push(step.wastebin);
                } else if (step.wastebin && step.wastebin.tile) {
                    warnings.push(step.wastebin.description);
                    tilesToDelete.push(step.wastebin);
                }
            });
            self.warning = self.wastebinWarning(warnings.join());
            var deleteObject = function(type, obj){
                if (type === 'resource') {
                    $.ajax({
                        url: arches.urls.api_resources(obj),
                        type: 'DELETE',
                        success: function(result) {
                            console.log('result', result);
                        }
                    });
                } else if (type === 'tile') {
                    $.ajax({
                        type: "DELETE",
                        url: arches.urls.tile,
                        data: JSON.stringify(obj)
                    }).done(function(response) {
                        console.log('deleted', obj.tileid);
                    }).fail(function(response) {
                        if (typeof onFail === 'function') {
                            console.log(response);
                        }
                    });
                }
            };

            self.alert(
                new AlertViewModel(
                    'ep-alert-red',
                    self.warning[0],
                    self.warning[1],
                    null,
                    function(){
                        resourcesToDelete.forEach(function(resource){deleteObject('resource', resource.resourceid);});
                        tilesToDelete.forEach(function(tile){deleteObject('tile', tile.tile);});
                        window.location.href = self.quitUrl;
                    }
                )
            );
        };

<<<<<<< HEAD
=======
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
                            if (complete && self.steps[i].autoAdvance()) self.next();
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
            var urlparams = JSON.parse(JSON.stringify(self.state)); //deep copy
            urlparams.steps = JSON.stringify(self.state.steps);
            history.pushState(null, '', window.location.pathname + '?' + $.param(urlparams));
        };

>>>>>>> 5167f1ff625d855ae1950d6236b6337aecaba660
        this.updateState = function(val) {
            var activeStep = val;
            var previousStep = self.previousStep();
            var resourceId;
            if (previousStep && previousStep.hasOwnProperty('defineStateProperties')) {
                self.state.steps[previousStep._index] = previousStep.defineStateProperties();
                self.state.steps[previousStep._index].complete = ko.unwrap(previousStep.complete);
                self.state.activestep = val._index;
                self.state.previousstep = previousStep._index;
                if (!self.state.resourceid) {
                    resourceId = !!previousStep.resourceid ? ko.unwrap(previousStep.resourceid) : null;
                    self.state.resourceid = resourceId;
                }
            }
            self.previousStep(activeStep);
        };

        this.canStepBecomeActive = function(step) {
            var canStepBecomeActive = false;
            
            if (step && !step.active()) {  /* prevents refresh if clicking on active tab */ 
                var previousStep = self.steps[step._index - 1];

                if (
                    step.complete() 
                    || ( previousStep && previousStep.complete() )
                    || self.canFinish() === true
                ) { 
                    canStepBecomeActive = true; 
                }
            }

            return canStepBecomeActive;
        };

        this.next = function(){
            var activeStep = self.activeStep();

            if (activeStep && (activeStep.complete() || !activeStep.required()) && activeStep._index < self.steps.length - 1) {
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
