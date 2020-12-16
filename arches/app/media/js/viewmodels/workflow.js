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
    WORKFLOWS_NAMESPACE = 'workflows';
    WORKFLOW_ID_URL_PARAM = 'workflow-id';

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
        this.ready.subscribe(function() {
            var components = _.unique(self.steps.map(function(step) {return step.component;}));
            require(components, function() { self.initialize(); });
        });

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
            /* if there's no workflowId in the params, let's set one */ 
            var cachedId = self.getWorkflowIdFromUrl();

            if (cachedId) {
                self.id(cachedId)
            }
            else {
                self.id(uuid.generate());
                self.setWorkflowIdToUrl();
            }
            
            self.createSteps(self.getStepIdsFromLocalStorage());

            /* set active step */ 
            if (self.state.activestep) {
                self.activeStep(self.steps[self.state.activestep]);
            }
            else if(self.steps.length > 0) {
                self.activeStep(self.steps[0]);
            }
        };

        this.createSteps = function(stepIds) {
            var stateStepCount = self.state.steps.length;
            var generatedStepIds = [];

            console.log('!!!AAA', stepIds)

            self.steps.forEach(function(step, i) {
                if (!(self.steps[i] instanceof Step)) {
                    step.workflow = self;
                    step.loading = self.loading;
                    step.alert = self.alert;



                    /* if stepIds exist for this workflow in localStorage, set correct value */ 
                    if (stepIds.length) { step.id = stepIds[i]; }

                    var newStep = new Step(step);
                    self.steps[i] = newStep;

                    /* if stepIds DO NOT exist for this workflow in localStorage, add id to accumulator */ 
                    if (!stepIds.length) { generatedStepIds.push(newStep.id()); }

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
            if (!stepIds.length) { self.setStepIdsToLocalStorage(generatedStepIds); }
        };

        this.getWorkflowIdFromUrl = function() {
            var searchParams = new URLSearchParams(window.location.search);
            return searchParams.get(WORKFLOW_ID_URL_PARAM);
        };
        
        this.setWorkflowIdToUrl = function() {
            var searchParams = new URLSearchParams(window.location.search);
            searchParams.set(WORKFLOW_ID_URL_PARAM, self.id());

            var newRelativePathQuery = `${window.location.pathname}?${searchParams.toString()}`;
            history.replaceState(null, '', newRelativePathQuery);
        };

        this.getStepIdsFromLocalStorage = function() {
            var workflows = JSON.parse(localStorage.getItem(WORKFLOWS_NAMESPACE));

            if (workflows && workflows[self.id()]) {
                return workflows[self.id()];
            }

            return [];
        };

        this.setStepIdsToLocalStorage = function(stepIds) {
            var workflows = JSON.parse(localStorage.getItem(WORKFLOWS_NAMESPACE));
            if (!workflows) { workflows = {}; }  /* create workflows namespace if it doesn't already exist */ 
                        
            workflows[self.id()] = stepIds;
            
            localStorage.setItem(WORKFLOWS_NAMESPACE, JSON.stringify(workflows));
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

        // this.restoreStateFromURL = function(){
        //     var urlparams = new window.URLSearchParams(window.location.search);
        //     var res = {};
        //     var pathArray = window.location.pathname.split('/');
        //     res.workflowid = pathArray[2];
        //     urlparams.forEach(function(v, k){res[k] = v;});
        //     res.steps = res.steps ? JSON.parse(res.steps) : [];
        //     this.state = res;
        // };

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

        // this.updateUrl = function() {
        //     //Updates the url with the parameters needed for the next step
        //     var urlparams = JSON.parse(JSON.stringify(this.state)); //deep copy
        //     urlparams.steps = JSON.stringify(this.state.steps);
        //     history.pushState(null, '', window.location.pathname + '?' + $.param(urlparams));
        // };

        this.foo = function() {

        };

        this.updateState = function(val) {
            //Collects information from the previous step and sets it to the URL
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
