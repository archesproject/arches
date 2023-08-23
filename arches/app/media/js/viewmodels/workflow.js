define([
    'jquery',
    'underscore',
    'knockout',
    'knockout-mapping',
    'arches',
    'uuid',
    'js-cookie',
    'viewmodels/alert',
    'viewmodels/workflow-step',
    'bindings/gallery',
    'bindings/scrollTo'
], function($, _, ko, koMapping, arches, uuid, Cookies, AlertViewModel, WorkflowStep) {
    const WORKFLOW_ID_LABEL = 'workflow-id';
    const STEP_ID_LABEL = 'workflow-step-id';
    const WORKFLOW_COMPONENT_ABSTRACTS_LABEL = 'workflow-component-abstracts';

    var Workflow = function(config) {
        var self = this;

        this.id = ko.observable();
        this.workflowName = ko.observable();

        this.hiddenWorkflowButtons = ko.observableArray();

        this.pan = ko.observable();
        this.alert = config.alert || ko.observable(null);
        this.quitUrl = config.quitUrl || arches.urls.search_home;
        this.plugin = config.plugin;
        this.isWorkflowFinished = ko.observable(false);
        
        this.stepConfig;  /* overwritten in workflow.js file */
        this.steps = ko.observableArray();
        this.stepids = [];
        
        this.activeStep = ko.observable();
        this.activeStep.subscribe(function(activeStep) {
            // activeStep.loading(true);

            self.setStepIdToUrl(activeStep);
            self.hiddenWorkflowButtons(activeStep.hiddenWorkflowButtons());
        });
        
        this.furthestValidStepIndex = ko.observable();
        this.furthestValidStepIndex.subscribe(function(index){
            if (index >= self.steps().length - 1) {
                self.isWorkflowFinished(true);
            } else {
                self.isWorkflowFinished(false);
            }
        });

        this.steps.subscribe(() => {
            this.furthestValidStepIndex.valueHasMutated();
        });
        
        this.initialize = function() {
            self.getWorkflowMetaData(self.componentName).then(async function(workflowJson) {
                self.workflowName(workflowJson.name);

                /* BEGIN workflow id logic */ 
                var currentWorkflowId = self.getWorkflowIdFromUrl();
                if (currentWorkflowId) {
                    self.id(currentWorkflowId);
                    await self.getWorkflowHistory();
                }
                else {
                    self.id(uuid.generate());
                    self.setWorkflowIdToUrl();
                    localStorage.removeItem(WORKFLOW_COMPONENT_ABSTRACTS_LABEL);
                }
                /* END workflow id logic */ 

                /* BEGIN workflow step creation logic */
                self.updateStepPath();
                
                var cachedStepId = self.getStepIdFromUrl();
                var cachedActiveStep = self.steps().find(function(step) {
                    return step.id() === cachedStepId;
                });

                if (cachedActiveStep) {
                    self.activeStep(cachedActiveStep);
                }
                else {
                    self.activeStep(self.steps()[0]);
                }
                /* END workflow step creation logic */

                /* Save Workflow History */
                self.saveWorkflowHistory();
            });
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
            }

            if (!workflowMetaDataLocalStorageData[workflowName][stepName]) {
                workflowMetaDataLocalStorageData[workflowName][stepName] = {};
            }
            
            workflowMetaDataLocalStorageData[workflowName][stepName][key] = value;

            localStorage.setItem(
                'workflow-metadata',
                JSON.stringify(workflowMetaDataLocalStorageData)
            );
        };

        this.createStep = function(stepData) {
            var stepName = ko.unwrap(stepData.name);
            
            /* if stepIds exist for this workflow in workflow history, set correct value */ 
            if (self.stepids && self.stepids[stepName]) {
                stepData.id = self.stepids[stepName];
            }
            
            stepData.informationBoxDisplayed = ko.observable(self.getInformationBoxDisplayedStateFromLocalStorage(stepName));
            stepData.informationBoxDisplayed.subscribe(function(val){
                self.setMetadataToLocalStorage(stepName, 'informationBoxDisplayed', val);
            });

            stepData.workflow = self;
            return new WorkflowStep(stepData);
        };

        this.saveActiveStep = function() {
            self.activeStep().save()
                .then(function(_data) {        
                    self.next();
                })
                .catch(function(error) {
                    console.error(error);
                });
        };

        this.staticSaveActiveStep = function() {
            self.activeStep().save()
                .catch(function(error) {
                    console.error(error);
                });
        };

        this.parseComponentPath = function(path) {
            var pathAsStringArray = path.slice(1, path.length - 1).split('][');

            return pathAsStringArray.map(function(string) {
                if (!isNaN(Number(string))) {
                    return Number(string);
                }
                else {
                    return string.slice(1, string.length - 1);
                }
            });
        };

        this.isValidComponentPath = function(path) {
            var matchingStep;

            if (typeof path === 'string') {  /* path instanceOf String returns false */
                var pathAsArray = self.parseComponentPath(path);

                matchingStep = self.steps().find(function(step) {
                    return step.name === pathAsArray[0];
                });
            }

            return Boolean(matchingStep);
        };

        this.getDataFromComponentPath = function(path) {
            var pathAsArray = self.parseComponentPath(path);

            var matchingStep = self.steps().find(function(step) {
                return step.name === pathAsArray[0];
            });

            var value;

            if (matchingStep) {
                var matchingWorkflowComponentAbstract = Object.keys(matchingStep.componentIdLookup()).reduce(function(acc, key) {
                    if (
                        matchingStep.workflowComponentAbstractLookup() 
                        && matchingStep.workflowComponentAbstractLookup()[key]
                        && matchingStep.workflowComponentAbstractLookup()[key].id() === matchingStep.componentIdLookup()[key]
                    ) {
                        acc[key] = matchingStep.workflowComponentAbstractLookup()[key];
                    }
                    return acc;
                }, {});

                value = matchingWorkflowComponentAbstract;
                
                var workflowAbstractComponent = matchingWorkflowComponentAbstract[pathAsArray[1]];
                
                if (workflowAbstractComponent) {
                    value = ko.unwrap(workflowAbstractComponent.savedData);
                    
                    var updatedPath = pathAsArray.slice(2);
                    
                    for (var chunk of updatedPath) {
                        if (value[chunk] !== undefined) {
                            value = value[chunk];
                        }
                    }
                }
            }

            return value;
        };

        this.toggleStepLockedState = function(stepName, locked) {
            var step = self.steps().find(function(step) { return ko.unwrap(step.name) === ko.unwrap(stepName); });
            if (step) {
                step.locked(locked);
            }
        };

        this.computedFurthestValidStepIndex = ko.computed(function() {
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
                    && self.steps()[furthestValidStepIndex]
                    && self.steps()[furthestValidStepIndex].complete()
                )
                || furthestValidStepIndex > 0
            ) { 
                furthestValidStepIndex += 1; 
            }

            if (furthestValidStepIndex !== self.furthestValidStepIndex()) {
                self.furthestValidStepIndex(furthestValidStepIndex);
            }
        });

        this.updateStepPath = function() {
            var steps = [];
            self.stepConfig.forEach(function(stepConfigData) {
                steps.push(
                    self.createStep(stepConfigData)
                );
            });

            var idx = 0;
            var currentStep;
            
            while (  /* while the current step is not the configured last step */ 
                ko.unwrap(steps[idx].name) !== ko.unwrap(self.stepConfig[self.stepConfig.length - 1].name)
            ) {
                currentStep = steps[idx];

                if (currentStep['stepInjectionConfig']) {
                    var childStep;
                    var defaultStepChoice = ko.unwrap(currentStep['stepInjectionConfig']['defaultStepChoice']);

                    if (currentStep.complete()) {
                        var stepData = currentStep['stepInjectionConfig']['injectionLogic'](currentStep);
                        if (stepData) {
                            childStep = self.createStep(stepData);
                        }
                        currentStep.locked(true);
                    }
                    else if (defaultStepChoice) {
                        childStep = self.createStep(defaultStepChoice);
                    }

                    if (childStep) {
                        var stepNameToInjectAfter = currentStep['stepInjectionConfig']['stepNameToInjectAfter'](currentStep);
                        var stepToInjectAfterIndex = steps.findIndex(function(step) {
                            return ko.unwrap(step.name) == stepNameToInjectAfter;
                        });

                        steps.splice(stepToInjectAfterIndex + 1, 0, childStep);
                    }
                }

                idx += 1;
            }

            /* 
                updates step indices
            */ 
            var updatedSteps = steps.map(function(step, index) {
                step['_index'] = index;
                return step;
            });

            self.steps(updatedSteps);
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
        
        this.saveWorkflowHistory = function() {
            const workflowid = self.id();

            var updatedStepNameToIdLookup = self.steps().reduce(function(acc, step) { 
                acc[ko.unwrap(step.name)] = step.id(); 
                return acc;
            }, {});

            const data = {
                workflowid: workflowid,
                workflowstepids: updatedStepNameToIdLookup,
                completed: false,
            };

            fetch(arches.urls.workflow_history + workflowid, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                },
                body: JSON.stringify(data),
            });
        };

        this.getWorkflowHistory = async function() {
            const workflowid = self.id();
            const response = await fetch(arches.urls.workflow_history + workflowid, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                },
            });
            const data = await response.json();
            self.stepids = data.workflowstepids;
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
            config.loading(true);
            $.ajax({
                type: "POST",
                url: arches.urls.transaction_reverse(self.id())
            }).then(function() {
                config.loading(false);
                window.location.href = self.quitUrl;
            });
        };

        this.finishWorkflow = function() {
            if (self.activeStep().hasUnsavedData()) {
                self.activeStep().save().then(function() {
                    window.location.assign(self.quitUrl);
                });
            }
            else {
                window.location.assign(self.quitUrl);
            }
        };

        this.quitWorkflow = function(){
            self.alert(
                new AlertViewModel(
                    'ep-alert-red',
                    'Are you sure you would like to delete this workflow?',
                    'All data created during the course of this workflow will be deleted.',
                    function(){}, //does nothing when canceled
                    self.reverseWorkflowTransactions,
                )
            );
        };

        this.next = function(){
            var activeStep = self.activeStep();

            if (activeStep.stepInjectionConfig) {
                self.updateStepPath();
            }

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
