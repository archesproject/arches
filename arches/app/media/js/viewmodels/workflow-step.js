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
        var self = this;

        this.id = ko.observable();
        this.workflowId = ko.observable(config.workflow ? config.workflow.id : null);

        this.isV2Workflow = config.workflow.v2;

        this.classUnvisited = 'workflow-step-icon';
        this.classActive = 'workflow-step-icon active';
        this.classComplete = 'workflow-step-icon complete';
        this.classCanAdavance = 'workflow-step-icon can-advance';

        this.icon = 'fa-chevron-circle-right';
        this.title = '';
        this.subtitle = '';
        this.description = '';

        this.informationBoxData = ko.observable();       

        this.hasDirtyTile = ko.observable(false);

        this.saving = ko.observable(false);
        this.loading = ko.observable(false);

        this.complete = ko.observable(false);

        this.required = ko.observable(ko.unwrap(config.required));
        this.autoAdvance = ko.observable(true);

        this.preSaveCallback = ko.observable();
        this.postSaveCallback = ko.observable();

        this.clearCallback = ko.observable();

        this.externalStepData = {};
        this.locked = ko.observable(false);
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

        this.value = ko.observable();
        this.value.subscribe(function(value) {
            var getResourceIdFromComponentData = function(componentData) {
                /* iterates over each component in layout */
                return Object.values(componentData).reduce(function(acc, componentDatum) {
                    /* most components store data for a single tile */ 
                    if (!acc && componentDatum instanceof Array && componentDatum.length === 1) {
                        if (componentDatum[0].resourceInstanceId) {
                            return componentDatum[0].resourceInstanceId;
                        } else if (componentDatum[0] instanceof Array && componentDatum[0][1].resourceInstanceId) {
                            return componentDatum[0][1].resourceInstanceId;
                        }
                    }
                    return acc;
                }, null);
            };

            /* if we have defined that this is part of a single-resource workflow, and that this step creates the desired resource */ 
            if (self.shouldtrackresource && !ko.unwrap(config.workflow.resourceId)) {
                if (value) {
                    var resourceId;
                     
                    if (value.resourceid) {  /* legacy newTileStep */
                        resourceId = value.resourceid
                    }
                    else {  /* component-based-step */
                        resourceId = getResourceIdFromComponentData(value);
                    }

                    config.workflow.resourceId(resourceId);
                } 
                else {
                    config.workflow.resourceId(null);
                }
            }
        });

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

        Object.keys(config).forEach(function(prop){
            if(prop !== 'workflow') {
                config[prop] = koMapping.fromJS(config[prop]);
            }
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

            var locked = self.getFromLocalStorage('locked');
            if (locked) {
                self.locked(locked);
            }

            /* cached value logic */ 
            var cachedValue = self.getFromLocalStorage('value');
            if (cachedValue) {
                self.value(cachedValue);
                self.complete(true);
            }

            /* set value subscription */ 
            self.value.subscribe(function(value) {
                self.setToLocalStorage('value', value);
            });

            self.locked.subscribe(function(value){
                self.setToLocalStorage("locked", value);
            });
    
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
                    resolve(self.value())
                });
            };
            var postSaveCallback = function() {
                // TODO: Refactor promise logic to pass down resolve
                return new Promise(function(resolve, _reject) {
                    var postSaveCallback = ko.unwrap(self.postSaveCallback);
                    resolve(postSaveCallback());
                });
            };
            
            return new Promise(function(resolve, _reject) {
                preSaveCallback().then(function(_preSaveCallbackData) {
                    writeToLocalStorage().then(function(_localStorageData) {
                        postSaveCallback().then(function(_postSaveCallbackData) {
                            resolve(self.value());
                        });
                    })
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

        this.iconClass = ko.computed(function(){
            var ret = '';
            if(this.active()){
                ret = this.classActive;
            }else if(this.complete()){
                ret = this.classComplete;
            }else {
                ret = this.classUnvisited;
            }
            return ret + ' ' + ko.unwrap(this.icon);
        }, this);

        this.saveOnQuit = function(){
            // to be implemented in an individual step
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
