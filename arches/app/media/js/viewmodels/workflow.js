define([
    'arches',
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'uuid',
    'viewmodels/alert',
    'viewmodels/workflow-step',
    'bindings/gallery',
    'bindings/scrollTo'
], function(arches, $, _, ko, koMapping, uuid, AlertViewModel, WorkflowStep) {
    WORKFLOW_LABEL = 'workflow';
    WORKFLOW_ID_LABEL = 'workflow-id';
    STEPS_LABEL = 'workflow-steps';
    STEP_ID_LABEL = 'workflow-step-id';
    STEP_IDS_LABEL = 'workflow-step-ids';

    var Workflow = function(config) {
        var self = this;

        this.id = ko.observable();
        this.resourceId = ko.observable();

        this.quitUrl = config.quitUrl || self.quitUrl || arches.urls.plugin('init-workflow');

        this.v2 = config.v2 || self.v2;
        
        this.steps = ko.observableArray();
        
        this.activeStep = ko.observable();
        this.activeStep.subscribe(function(activeStep) {
            self.setStepIdToUrl(activeStep);
        });
        
        this.isWorkflowFinished = ko.observable(false);
        
        this.furthestValidStepIndex = ko.observable();
        this.furthestValidStepIndex.subscribe(function(index){
            if (index >= self.steps().length - 1) {
                self.isWorkflowFinished(true)
            }
        });
        
        this.pan = ko.observable();
        
        this.hoverStep = ko.observable();  // legacy DO NOT USE
        this.ready = ko.observable(false);  // legacy  DO NOT USE

        this.workflowName = ko.observable();
        
        this.alert = config.alert || ko.observable(null);
        this.quitUrl = arches.urls.home;

        this.warning = '';

        this.initialize = function() {
            /* BEGIN workflow metadata logic */ 
            if (self.componentName) {
                self.getWorkflowMetaData(self.componentName).then(function(workflowJson) {
                    self.workflowName(workflowJson.name);
                });
            }
            /* END workflow metadata logic */ 

            /* BEGIN workflow id logic */ 
            var currentWorkflowId = self.getWorkflowIdFromUrl();
            if (currentWorkflowId) {
                self.id(currentWorkflowId)
            }
            else {
                self.id(uuid.generate());
                self.setWorkflowIdToUrl();
            }
            /* END workflow id logic */ 

            /* BEGIN workflow step creation logic */ 
            if (self.getFromLocalStorage(WORKFLOW_ID_LABEL) !== self.id()) {
                self.setToLocalStorage(WORKFLOW_ID_LABEL, self.id());
                /* remove step data created by previous workflow from localstorage */
                localStorage.removeItem(STEPS_LABEL);  
                localStorage.removeItem(STEP_IDS_LABEL);  
            }

            var cachedStepId = self.getStepIdFromUrl();

            var seedStep = self.createStep(self.stepConfig[0]);
            self.steps([seedStep]);
            self.activeStep(seedStep);  /* `self.updatePath() requires an activeStep */

            self.updateStepIndices();
            self.updateStepPath();

            var cachedActiveStep = self.steps().find(function(step) {
                return step.id() === cachedStepId;
            });

            if (cachedActiveStep) {
                self.activeStep(cachedActiveStep);
            }
            /* END workflow step creation logic */ 
        };
        
        this.wastebinWarning = function(val){
            if (val === '') {
                return [[arches.translations.workflowWastbinWarning3],[arches.translations.workflowWastbinWarning2]];
            } else {
                return [[arches.translations.workflowWastbinWarning.replace("${val}", val)],[arches.translations.workflowWastbinWarning2]];
            }
        };

        this.updatePan = function(val){
            if (this.pan() !== val) {
                this.pan(val);
            } else {
                this.pan.valueHasMutated();
            }
        };

        this.getInformationBoxDisplayedStateFromLocalStorage = function(stepName) {
            return self.getMetadataFromLocalStorage(stepName, 'informationBoxDisplayed');
        };

        this.getMetadataFromLocalStorage = function(stepName, key) {
            var workflowsMetadataLocalStorageData = JSON.parse(localStorage.getItem('workflow-metadata')) || {};
            var workflowName = ko.unwrap(self.workflowName);
            if (workflowsMetadataLocalStorageData[workflowName] && workflowsMetadataLocalStorageData[workflowName][stepName]) {
                return workflowsMetadataLocalStorageData[workflowName][stepName][key];
            }
        };

        this.setMetadataToLocalStorage = function(stepName, key, value) {
            var workflowMetaDataLocalStorageData = JSON.parse(localStorage.getItem('workflow-metadata')) || {};
            var workflowName = ko.unwrap(self.workflowName);

            if (!workflowMetaDataLocalStorageData[workflowName]) {
                workflowMetaDataLocalStorageData[workflowName] = {};
            };

            if (!workflowMetaDataLocalStorageData[workflowName][stepName]) {
                workflowMetaDataLocalStorageData[workflowName][stepName] = {};
            };
            
            workflowMetaDataLocalStorageData[workflowName][stepName][key] = value;

            localStorage.setItem(
                'workflow-metadata',
                JSON.stringify(workflowMetaDataLocalStorageData)
            );
        };

        this.createStep = function(stepData) {
            var stepNameToIdLookup = self.getFromLocalStorage(STEP_IDS_LABEL);

            var stepName = ko.unwrap(stepData.name);
            
            /* if stepIds exist for this workflow in localStorage, set correct value */ 
            if (stepNameToIdLookup[stepName]) {
                stepData.id = stepNameToIdLookup[stepName];
            }
            
            stepData.informationBoxDisplayed = ko.observable(self.getInformationBoxDisplayedStateFromLocalStorage(stepName));
            stepData.informationBoxDisplayed.subscribe(function(val){
                self.setMetadataToLocalStorage(stepName, 'informationBoxDisplayed', val);
            });

            stepData.workflow = self;
            return new WorkflowStep(stepData);
        };

        this.updateStepIndices = function() {
            var steps = self.steps();

            var updatedSteps = steps.map(function(step, index) {
                step['_index'] = index;
                return step;
            });

            self.steps(updatedSteps);
        };

        this.saveActiveStep = function() {
            return new Promise(function(resolve, _reject) {
                self.activeStep().save().then(function(data) {            
                    resolve(data);
                });
            });
        };

        this.getStepData = function(stepName) {
            return new Promise(function(resolve) {
                /* ONLY to be used as intermediary for when a step needs data from a different step in the workflow */
                var step = self.steps().find(function(step) { return ko.unwrap(step.name) === ko.unwrap(stepName); });

                if (step) { 
                    if (step.saving()) {
                        var savingSubscription = step.saving.subscribe(function(saving) {
                            if (!saving) {
                                savingSubscription.dispose(); /* self-disposing subscription */
                                resolve({ [step.name()]: step.value() }); 
                            }
                        });
                    }
                    else {
                        resolve({ [step.name()]: step.value() });
                    }
                }
                else {
                    resolve(null);
                }
            });
        };

        this.toggleStepLockedState = function(stepName, locked) {
            var step = self.steps().find(function(step) { return ko.unwrap(step.name) === ko.unwrap(stepName); });
            if (step) {
                step.locked(locked);
            }
        }

        this.getStepIdFromUrl = function() {
            var searchParams = new URLSearchParams(window.location.search);
            return searchParams.get(STEP_ID_LABEL);
        };

        this.setStepIdToUrl = function(step) {
            var searchParams = new URLSearchParams(window.location.search);
            searchParams.set(STEP_ID_LABEL, step.id());

            var newRelativePathQuery = `${window.location.pathname}?${searchParams.toString()}`;
            history.pushState(null, '', newRelativePathQuery);
        };

        this.getFurthestValidStepIndex = function() {
            /*
                valid index is the index directly after the furthest completed step
                or furthest non-required step chained to the beginning/most-completed step
            */ 

            var furthestValidStepIndex = self.furthestValidStepIndex() || 0;
            var startIdx = 0;

            /* furthest completed step index */ 
            self.steps().forEach(function(step) {
                if (ko.unwrap(step.complete)) {
                    startIdx = step._index;
                }
            });

            /* furthest non-required step directly after furthest completed step */ 
            for (var i = startIdx; i < self.steps().length; i++) {
                var step = self.steps()[i];

                if (ko.unwrap(step.complete) || !ko.unwrap(step.required)) {
                    furthestValidStepIndex = step._index;
                }
                else { break; }
            }

            /* add index position for furthest valid index if not incomplete beginning step */ 
            if (
                (
                    furthestValidStepIndex === 0 
                    && self.steps()[furthestValidStepIndex].complete()
                )
                || furthestValidStepIndex > 0
            ) { 
                furthestValidStepIndex += 1; 
            }

            if (furthestValidStepIndex !== self.furthestValidStepIndex()) {
                self.furthestValidStepIndex(furthestValidStepIndex);
            }
        };

        this.updateStepPath = function() {
            var findFurthestValidConfiguredStepIndex = function() {
                /* 
                    because `self.steps()` idx can be higher than `self.stepConfig` idx,
                    we backtrack from active step to first step to appear in `self.stepConfig`
                */ 
                var stepIdx = self.activeStep()._index;
                var foundStepConfigStepIdx = -1;
                
                while (stepIdx > -1) {
                    var step = self.steps()[stepIdx];
                    var foundStepConfigStep = self.stepConfig.find(function(stepConfigStep) {
                        return stepConfigStep.name() === step.name();
                    });

                    if (foundStepConfigStep) {
                        foundStepConfigStepIdx = stepIdx;
                    }

                    stepIdx -= 1;
                }

                return foundStepConfigStepIdx;
            };

            var stepConfigIdx = findFurthestValidConfiguredStepIndex();
            var furthestValidConfiguredStep = self.steps()[stepConfigIdx];
            
            var remainingStepPath = [];
            var step;

            while (
                !step 
                || step.name() !== ko.unwrap(self.stepConfig[self.stepConfig.length - 1].name)
                /* runs until it creates the last step in the step configuration */ 
            ) {
                var parentStep = remainingStepPath.length ? remainingStepPath[remainingStepPath.length - 1] : furthestValidConfiguredStep;

                if (parentStep && parentStep['stepInjectionConfig']) {
                    if (parentStep.complete()) {
                        step = self.createStep(parentStep['stepInjectionConfig']['injectionLogic']());
                    }
                    else {
                        step = self.createStep(ko.unwrap(parentStep['stepInjectionConfig']['defaultStepChoice']));
                    }
                }
                else {
                    stepConfigIdx += 1;
                    step = self.createStep(self.stepConfig[stepConfigIdx]);
                }
    
                remainingStepPath.push(step);
            }

            self.steps.splice(findFurthestValidConfiguredStepIndex() + 1, remainingStepPath.length, ...remainingStepPath);

            var updatedStepNameToIdLookup = self.steps().reduce(function(acc, step) { 
                acc[step.name()] = step.id(); 
                return acc;
            }, {});

            self.setToLocalStorage(STEP_IDS_LABEL, updatedStepNameToIdLookup);
            self.updateStepIndices();
            self.getFurthestValidStepIndex();
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

        this.setToLocalStorage = function(key, value) {
            var workflowLocalStorageData = JSON.parse(localStorage.getItem(WORKFLOW_LABEL)) || {};
            
            workflowLocalStorageData[key] = value;

            localStorage.setItem(
                WORKFLOW_LABEL, 
                JSON.stringify(workflowLocalStorageData)
            );
        };

        this.getFromLocalStorage = function(key) {
            var localStorageData = JSON.parse(localStorage.getItem(WORKFLOW_LABEL));

            if (localStorageData) {
                return localStorageData[key];
            }
        };

        this.getWorkflowMetaData = function(pluginJsonFileName) {
            return new Promise(function(resolve, _reject) {
                $.ajax({
                    type: "GET",
                    url: arches.urls.plugin(pluginJsonFileName),
                    data: { "json":true },
                    context: self,
                    success: function(workflowJson){ resolve(workflowJson); }
                });
            });
        };

        this.reverseWorkflowTransactions = function() {
            $.ajax({
                type: "POST",
                url: arches.urls.transaction_reverse(self.id())
            });
        };

        this.finishWorkflow = function() {
            if (self.isWorkflowFinished()) { self.activeStep(self.steps()[self.steps().length - 1]); }
        };

        this.finishTabbedWorkflow = function() { //TODO: promise chain needs to be implemented later
            if (self.activeStep().hasDirtyTile()) {
                self.activeStep().save()
            }
            self.steps().forEach(function(step){
                step.saveOnQuit();
            })
            window.location.assign(self.quitUrl);
        };

        this.quitWorkflow = function(){
            var resourcesToDelete = [];
            var tilesToDelete = [];
            var warnings = []

            self.steps().forEach(function(step) {
                var wastebin = step.wastebin;

                if (wastebin) {
                    if (ko.unwrap(wastebin.resources)) {
                        var resources = ko.mapping.toJS(wastebin.resources);
                        resources.forEach(function(resource) {
                            warnings.push(resource.description);
                            resourcesToDelete.push(resource);
                        })
                    }
                    if (ko.unwrap(wastebin.resourceid)) {
                        warnings.push(ko.unwrap(wastebin.description));
                        resourcesToDelete.push(ko.mapping.toJS(wastebin));
                    } else if (ko.unwrap(wastebin.tile)) {
                        warnings.push(ko.unwrap(wastebin.description));
                        tilesToDelete.push(ko.mapping.toJS(wastebin));
                    }
                }
            });

            self.warning = self.wastebinWarning(warnings.join(', '));
            
            var deleteObject = function(type, obj){
                if (type === 'resource') {
                    console.log(obj);
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
                    function(){}, //does nothing when canceled
                    function(){
                        resourcesToDelete.forEach(function(resource){deleteObject('resource', resource.resourceid);});
                        tilesToDelete.forEach(function(tile){deleteObject('tile', tile.tile);});
                        self.reverseWorkflowTransactions();
                        window.location.href = self.quitUrl;
                    }
                )
            );
        };

        this.next = function(){
            var activeStep = self.activeStep();

            if ((!activeStep.required() || activeStep.complete()) && activeStep._index < self.steps().length - 1) {
                self.activeStep(self.steps()[activeStep._index + 1]);
            }
        };

        this.back = function(){
            var activeStep = self.activeStep();

            if (activeStep && activeStep._index > 0) {
                self.activeStep(self.steps()[activeStep._index - 1]);
            }
        };

        self.initialize();
    };

    return Workflow;
});
