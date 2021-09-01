define([
    'knockout',
    'underscore',
    'knockout-mapping',
    'uuid',
    'views/components/workflows/workflow-component-abstract',
    'views/components/workflows/component-based-step',
], function(ko, _, koMapping, uuid, WorkflowComponentAbstract) {
    STEPS_LABEL = 'workflow-steps';
    STEP_ID_LABEL = 'workflow-step-id';

    var WorkflowStep = function(config) {
        _.extend(this, config);

        var self = this;

        this.id = ko.observable();
        this.workflowId = ko.observable(config.workflow ? config.workflow.id : null);

        this.parameters = config.parameters;

        this.informationBoxData = ko.observable();

        this.componentBasedStepClass = ko.unwrap(config.workflowstepclass);
        this.hiddenWorkflowButtons = ko.observableArray(config.hiddenWorkflowButtons || []);
        
        this.required = ko.observable(ko.unwrap(config.required));
        this.loading = ko.observable(false);
        this.saving = ko.observable(false);
        this.complete = ko.observable(false);
        
        // this.value = ko.observable();
        this.hasDirtyTile = ko.observable(false);

        this.preSaveCallback = ko.observable();
        this.postSaveCallback = ko.observable();
        this.clearCallback = ko.observable();

        this.clearCallback = ko.observable();

        this.lockableExternalSteps = config.lockableExternalSteps || [];

        this.active = ko.computed(function() {
            return config.workflow.activeStep() === this;
        }, this);

        this.locked = ko.observable(false);
        this.locked.subscribe(function(value){
            self.setToLocalStorage("locked", value);
        });

        /* 
            `pageLayout` is an observableArray of arrays representing section Information ( `sectionInfo` ).

            `sectionInfo` is an array where the first item is the `sectionTitle` parameter, and the second 
            item is an array of `uniqueInstanceName`.
        */ 
        this.pageLayout = ko.observableArray();

        /*
            `workflowComponentAbstractLookup` is an object where we pair a `uniqueInstanceName` 
            key to `WorkflowComponentAbstract` class objects.
        */ 
        this.workflowComponentAbstractLookup = ko.observable({});

        this.componentIdLookup = ko.observable();
        this.componentIdLookup.subscribe(function(componentIdLookup) {
            self.setToLocalStorage('componentIdLookup', componentIdLookup)
        });



        this.initialize = function() {
            /* cached ID logic */ 
            var cachedId = ko.unwrap(config.id);
            if (cachedId) {
                self.id(cachedId)
            }
            else {
                self.id(uuid.generate());
            }

            /* cached workflowComponentAbstract logic */ 
            var cachedComponentIdLookup = self.getFromLocalStorage('componentIdLookup');
            if (cachedComponentIdLookup) {
                self.componentIdLookup(cachedComponentIdLookup);
            }

            /* step lock logic */ 
            var locked = self.getFromLocalStorage('locked');
            if (locked) {
                self.locked(locked);
            }
    
            /* cached informationBox logic */
            this.setupInformationBox();

            ko.toJS(self.layoutSections).forEach(function(layoutSection) {
                var uniqueInstanceNames = [];
    
                layoutSection.componentConfigs.forEach(function(componentConfigData) {
                    uniqueInstanceNames.push(componentConfigData.uniqueInstanceName);
                    
                    var workflowComponentAbstractId;
    
                    if (self.componentIdLookup() && self.componentIdLookup()[componentConfigData.uniqueInstanceName]) {
                        workflowComponentAbstractId = self.componentIdLookup()[componentConfigData.uniqueInstanceName];
                    }
    
                    console.log('ds90', workflowComponentAbstractId, self.componentIdLookup(), self.componentIdLookup())
    
                    self.updateWorkflowComponentAbstractLookup(componentConfigData, workflowComponentAbstractId);
                });
    
                var sectionInfo = [layoutSection.sectionTitle, uniqueInstanceNames];
    
                self.pageLayout.push(sectionInfo);
            });

            console.log(config)
        };

        this.updateWorkflowComponentAbstractLookup = function(workflowComponentAbtractData, workflowComponentAbstractId) {
            var workflowComponentAbstractLookup = self.workflowComponentAbstractLookup();

            // var workflowComponentAbstract = new WorkflowComponentAbstract(
                // workflowComponentAbtractData,
            //     workflowComponentAbstractId,
            //     config.workflow.isValidComponentPath,
            //     config.workflow.getDataFromComponentPath,
            //     config.title,
            //     self.isStepSaving,
            //     self.locked,
            //     self.lockExternalStep,
            //     self.lockableExternalSteps,
            //     self.workflowId,
            //     self.alert,
            //     self.outerSaveOnQuit,
            // );

        // console.log("90ds", componentData, workflowComponentAbstractId, isValidComponentPath, getDataFromComponentPath, title, isStepSaving, locked, lockExternalStep, lockableExternalSteps, workflowId, alert, outerSaveOnQuit)


            var workflowComponentAbstract = {
                componentData: workflowComponentAbtractData,
                workflowComponentAbstractId: workflowComponentAbstractId,
                isValidComponentPath: config.workflow.isValidComponentPath,
                getDataFromComponentPath: config.workflow.getDataFromComponentPath,
                title: config.title,
                isStepSaving: self.isStepSaving,
                locked: self.locked,
                lockExternalStep: self.lockExternalStep,
                lockableExternalSteps: self.lockableExternalSteps,
                workflowId: self.workflowId,
                alert: self.alert,
                outerSaveOnQuit: self.outerSaveOnQuit,
            };

            console.log('!!!!', workflowComponentAbstract)

            // /* 
            //     checks if all `workflowComponentAbstract`s have saved data if a single `workflowComponentAbstract` 
            //     updates its data, neccessary for correct aggregate behavior
            // */
            // workflowComponentAbstract.hasUnsavedData.subscribe(function() {
            //     var hasUnsavedData = Object.values(self.workflowComponentAbstractLookup()).reduce(function(acc, workflowComponentAbstract) {
            //         if (workflowComponentAbstract.hasUnsavedData()) {
            //             acc = true;
            //         } 
            //         return acc;
            //     }, false);

            //     self.hasUnsavedData(hasUnsavedData);
            // });

            workflowComponentAbstractLookup[workflowComponentAbtractData.uniqueInstanceName] = workflowComponentAbstract;

            self.workflowComponentAbstractLookup(workflowComponentAbstractLookup);
        };

        // this.save = function() {};  /* overwritten in component-based-step */
        
        this.save = function() {
            var preSaveCallback = function() {
                return new Promise(function(resolve, _reject) {
                    var preSaveCallback = ko.unwrap(self.preSaveCallback);
                    preSaveCallback(resolve);
                });
            };
            // var writeToLocalStorage = function() {
            //     return new Promise(function(resolve, _reject) {
            //         self.setToLocalStorage('value', self.value());
            //         resolve(self.value());
            //     });
            // };
            var postSaveCallback = function() {
                // TODO: Refactor promise logic to pass down resolve
                return new Promise(function(resolve, _reject) {
                    var postSaveCallback = ko.unwrap(self.postSaveCallback);

                    if (postSaveCallback) {
                        resolve(postSaveCallback());
                    }
                    else {
                        resolve(null);
                    }
                });
            };
            
            return new Promise(function(resolve, _reject) {
                preSaveCallback().then(function(_preSaveCallbackData) {
                    // writeToLocalStorage().then(function(_localStorageData) {
                        postSaveCallback().then(function(_postSaveCallbackData) {
                            resolve(self.value());
                        });
                    // });
                });
            });
        };

        this.clear = function() {
            if (self.hasDirtyTile()) {
                if (ko.unwrap(self.tile)) {
                    self.tile().reset();
                }

                if (ko.unwrap(self.clearCallback)) {
                    self.clearCallback()();
                }
            }
        }

        this.setToLocalStorage = function(key, value) {
            var allStepsLocalStorageData = JSON.parse(localStorage.getItem(STEPS_LABEL)) || {};

            if (!allStepsLocalStorageData[ko.unwrap(self.name)]) {
                allStepsLocalStorageData[ko.unwrap(self.name)] = {};
            }

            allStepsLocalStorageData[ko.unwrap(self.name)][key] = value ? koMapping.toJSON(value) : value;

            localStorage.setItem(
                STEPS_LABEL, 
                JSON.stringify(allStepsLocalStorageData)
            );
        };

        this.getFromLocalStorage = function(key) {
            var allStepsLocalStorageData = JSON.parse(localStorage.getItem(STEPS_LABEL)) || {};

            if (allStepsLocalStorageData[ko.unwrap(self.name)] && typeof allStepsLocalStorageData[ko.unwrap(self.name)][key] !== "undefined") {
                return JSON.parse(allStepsLocalStorageData[ko.unwrap(self.name)][key]);
            }
        };

        this.toggleInformationBox = function() {
            var informationBoxData = self.informationBoxData();
            var isDisplayed = informationBoxData['displayed'];

            informationBoxData['displayed'] = !isDisplayed;
            self.informationBoxData(informationBoxData);

            config.informationBoxDisplayed(!isDisplayed);
        };

        this.setupInformationBox = function() {
            if (config.informationBoxDisplayed && config.informationboxdata) {
                var isDisplayed = true;
                if (config.informationBoxDisplayed() !== undefined){
                    isDisplayed = config.informationBoxDisplayed();
                }
                self.informationBoxData({
                    displayed: isDisplayed,
                    heading: config.informationboxdata['heading'],
                    text: config.informationboxdata['text'],
                })
            }
        };

        this.lockExternalStep = function(step, locked) {
            if (self.lockableExternalSteps.indexOf(step) > -1){
                config.workflow.toggleStepLockedState(step, locked);
            } else {
                throw new Error("The step, " + step + ", cannot be locked")
            }
        };

        this.initialize();
    };
    
    /* only register template here, params are passed at the workflow level */ 
    ko.components.register('workflow-step', {
        template: {
            require: 'text!templates/views/components/plugins/workflow-step.htm'
        }
    });

    return WorkflowStep;
});
