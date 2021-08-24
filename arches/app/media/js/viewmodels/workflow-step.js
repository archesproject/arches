define([
    'knockout',
    'underscore',
    'knockout-mapping',
    'uuid',
    'views/components/workflows/component-based-step',
], function(ko, _, koMapping, uuid) {
    STEPS_LABEL = 'workflow-steps';
    STEP_ID_LABEL = 'workflow-step-id';

    var WorkflowStep = function(config) {
        _.extend(this, config);

        var self = this;

        this.id = ko.observable();
        this.workflowId = ko.observable(config.workflow ? config.workflow.id : null);


        this.isV2Workflow = config.workflow.v2;  // TODO: remove this


        this.informationBoxData = ko.observable();       
        
        this.required = ko.observable(ko.unwrap(config.required));
        this.loading = ko.observable(false);
        this.saving = ko.observable(false);
        this.complete = ko.observable(false);
        
        this.value = ko.observable();
        this.hasDirtyTile = ko.observable(false);

        this.preSaveCallback = ko.observable();
        this.postSaveCallback = ko.observable();
        this.clearCallback = ko.observable();

        this.clearCallback = ko.observable();

        this.externalStepData = {};
        this.lockableExternalSteps = config.lockableExternalSteps || [];

        /* BEGIN coerce externalStepData */ 
        var externalStepSourceData = ko.unwrap(config.externalstepdata) || {};
        Object.keys(externalStepSourceData).forEach(function(key) {
            if (key !== '__ko_mapping__') {
                self.externalStepData[key] = {
                    stepName: externalStepSourceData[key]
                };
            }
        });
        /* END coerce externalStepData */

        this.active = ko.computed(function() {
            return config.workflow.activeStep() === this;
        }, this);
        this.active.subscribe(function(active) {
            self.loading(true);
            if (active) { 
                self.getExternalStepData().then(function(externalStepData){
                    if (externalStepData) {
                        Object.entries(self.externalStepData).forEach(function([externalStepReferenceName, value]) {
                            self.externalStepData[externalStepReferenceName]['data'] = externalStepData[ko.unwrap(value.stepName)];
                        });
                    }
                    self.loading(false);
                });
            }
        });

        this.locked = ko.observable(false);
        this.locked.subscribe(function(value){
            self.setToLocalStorage("locked", value);
        });

        this.initialize = function() {
            _.extend(this, config);

            /* cached ID logic */ 
            var cachedId = ko.unwrap(config.id);
            if (cachedId) {
                self.id(cachedId)
            }
            else {
                self.id(uuid.generate());
            }

            /* cached value logic */ 
            var cachedValue = self.getFromLocalStorage('value');
            if (cachedValue) {
                self.value(cachedValue);
                self.complete(true);
            }

            /* step lock logic */ 
            var locked = self.getFromLocalStorage('locked');
            if (locked) {
                self.locked(locked);
            }
    
            /* cached informationBox logic */
            this.setupInformationBox();
        };
        
        this.save = function() {
            var preSaveCallback = function() {
                return new Promise(function(resolve, _reject) {
                    var preSaveCallback = ko.unwrap(self.preSaveCallback);
                    preSaveCallback(resolve);
                });
            };
            var writeToLocalStorage = function() {
                return new Promise(function(resolve, _reject) {
                    self.setToLocalStorage('value', self.value());
                    resolve(self.value());
                });
            };
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
                    writeToLocalStorage().then(function(_localStorageData) {
                        postSaveCallback().then(function(_postSaveCallbackData) {
                            resolve(self.value());
                        });
                    });
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

            if (!allStepsLocalStorageData[self.id()]) {
                allStepsLocalStorageData[self.id()] = {};
            }

            allStepsLocalStorageData[self.id()][key] = value ? koMapping.toJSON(value) : value;

            localStorage.setItem(
                STEPS_LABEL, 
                JSON.stringify(allStepsLocalStorageData)
            );
        };

        this.getFromLocalStorage = function(key) {
            var allStepsLocalStorageData = JSON.parse(localStorage.getItem(STEPS_LABEL)) || {};

            if (allStepsLocalStorageData[self.id()] && typeof allStepsLocalStorageData[self.id()][key] !== "undefined") {
                return JSON.parse(allStepsLocalStorageData[self.id()][key]);
            }
        };

        this.getExternalStepData = function() {
            return new Promise(function(resolve, _reject) {
                var promises = [];

                Object.keys(self.externalStepData).forEach(function(key) {
                    promises.push(config.workflow.getStepData(externalStepSourceData[key]));
                });

                if (promises.length) {
                    Promise.all(promises).then(function(resolvedPromiseData) {
                        resolve(
                            resolvedPromiseData.reduce(function(acc, resolvedPromiseDatum) {
                                if (resolvedPromiseDatum) {
                                    Object.keys(resolvedPromiseDatum).forEach(function(key) {
                                        acc[key] = resolvedPromiseDatum[key];
                                    });
                                }
                                return acc;
                            }, {})
                        );
                    });
                }
                else {
                    resolve(null);
                }
            });
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
