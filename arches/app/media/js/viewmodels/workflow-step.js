define([
    'knockout',
    'underscore',
    'knockout-mapping',
    'arches',
    'uuid',
    'js-cookie',
    'views/components/workflows/workflow-component-abstract',
    'templates/views/components/plugins/workflow-step.htm'
], function(ko, _, koMapping, arches, uuid, Cookies, WorkflowComponentAbstract, workflowStepTemplate) {
    const STEPS_LABEL = 'workflow-steps';
    const COMPONENT_ID_LOOKUP_LABEL = 'componentIdLookup';

    var WorkflowStep = function(config) {
         
        
        _.extend(this, config);

        var self = this;

         
        this.id = ko.observable();
        this.workflowId = ko.observable(config.workflow ? config.workflow.id : null);

        this.parameters = config.parameters;

        this.informationBoxData = ko.observable();

        this.componentBasedStepClass = ko.unwrap(config.workflowstepclass);
        this.hiddenWorkflowButtons = ko.observableArray(config.hiddenWorkflowButtons || []);

        /* 
            `pageLayout` is an observableArray of arrays representing section Information ( `sectionInfo` ).

            `sectionInfo` is an array where the first item is the `sectionTitle` parameter, and the second 
            item is an array of `uniqueInstanceName`.
        */ 
        this.pageLayout = ko.observableArray();
        this.workflowComponentAbstractLookup = ko.observable({});

        this.componentIdLookup = ko.observable();
        this.componentIdLookup.subscribe(function(componentIdLookup) {
            self.setToWorkflowHistory(COMPONENT_ID_LOOKUP_LABEL, componentIdLookup);
        });


        this.required = ko.observable(ko.unwrap(config.required));
        this.saveWithoutProgressing = ko.observable(ko.unwrap(config.saveWithoutProgressing));
        this.loading = ko.observable(false);
        this.saving = ko.observable(false);

        this.lockableExternalSteps = config.lockableExternalSteps || [];

        this.complete = ko.computed(function() {
            var complete = true; 
            
            Object.values(self.workflowComponentAbstractLookup()).forEach(function(workflowComponentAbstract) {
                if (!workflowComponentAbstract.complete()) {
                    complete = false;
                }
            });

            return complete;
        });

        /* 
            checks if all `workflowComponentAbstract`s have saved data if a single `workflowComponentAbstract` 
            updates its data, neccessary for correct aggregate behavior
        */
        this.hasUnsavedData = ko.computed(function() {
            return Object.values(self.workflowComponentAbstractLookup()).reduce(function(acc, workflowComponentAbstract) {
                if (workflowComponentAbstract.hasUnsavedData()) {
                    acc = true;
                } 
                return acc;
            }, false);
        });

        this.active = ko.computed(function() {
            return config.workflow.activeStep() === this;
        }, this);

        this.locked = ko.observable(false);
        this.locked.subscribe(function(value){
            self.setToLocalStorage("locked", value);
        });

        this.initialize = async function() {
            /* cached ID logic */ 
            var cachedId = ko.unwrap(config.id);
            if (cachedId) {
                self.id(cachedId);
            }
            else {
                self.id(uuid.generate());
            }

            /* workflow ID logic */ 
            if (config.workflow && ko.unwrap(config.workflow.id)) {
                self.workflowId = ko.unwrap(config.workflow.id);
            }

            /* cached workflowComponentAbstract logic */ 
            const stepData = config.allStepsData[ko.unwrap(self.name)];
            if (stepData) {
                self.componentIdLookup(stepData[COMPONENT_ID_LOOKUP_LABEL]);
            }

            /* step lock logic */ 
            var locked = self.getFromLocalStorage('locked');
            if (locked) {
                self.locked(locked);
            }
    
            /* cached informationBox logic */
            this.setupInformationBox();

            /* build page layout */ 
            for (const layoutSection of ko.toJS(self.layoutSections)) {
                var uniqueInstanceNames = [];

                for (const componentConfigData of layoutSection.componentConfigs) {
                    uniqueInstanceNames.push(componentConfigData.uniqueInstanceName);
                    self.updateWorkflowComponentAbstractLookup(componentConfigData, stepData);
                }
                self.pageLayout.push([layoutSection.sectionTitle, uniqueInstanceNames]);
            }

            /* assigns componentIdLookup to self, which updates workflow history */
            var componentIdLookup = Object.keys(self.workflowComponentAbstractLookup()).reduce(function(acc, key) {
                acc[key] = self.workflowComponentAbstractLookup()[key].id();
                return acc;
            }, {});

            self.componentIdLookup(componentIdLookup);
        };

        this.updateWorkflowComponentAbstractLookup = function(workflowComponentAbtractData, stepData) {
            var workflowComponentAbstractLookup = self.workflowComponentAbstractLookup();
            var workflowComponentAbstractId;

            if (stepData) {
                const componentIdLookup = stepData[COMPONENT_ID_LOOKUP_LABEL];
                if (componentIdLookup) {
                    workflowComponentAbstractId = componentIdLookup[workflowComponentAbtractData.uniqueInstanceName];
                }
            }

            var workflowComponentAbstract = new WorkflowComponentAbstract({
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
                isStepActive: self.active,
            });

            workflowComponentAbstractLookup[workflowComponentAbtractData.uniqueInstanceName] = workflowComponentAbstract;

            self.workflowComponentAbstractLookup(workflowComponentAbstractLookup);
        };

        this.save = function() {
            self.saving(true);

            return new Promise(function(resolve, reject) {
                var savePromises = [];
            
                Object.values(self.workflowComponentAbstractLookup()).forEach(function(workflowComponentAbstract) {
                    savePromises.push(new Promise(function(resolve, reject) {
                        workflowComponentAbstract._saveComponent(resolve, reject);
                    }));
                });
    
                Promise.all(savePromises)
                    .then(function(values) {
                        resolve(...values);
                    })
                    .catch(function(error) {
                        reject(error);
                    })
                    .finally(
                        self.saving(false)
                    );
            });
        };

        this.undo = function() {
            return new Promise(function(resolve, _reject) {
                var resetPromises = [];
            
                Object.values(self.workflowComponentAbstractLookup()).forEach(function(workflowComponentAbstract) {
                    resetPromises.push(new Promise(function(resolve, _reject) {
                        workflowComponentAbstract._resetComponent(resolve);
                    }));
                });
    
                Promise.all(resetPromises).then(function(values) {
                    resolve(...values);
                });
            });
        };

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

        this.setToWorkflowHistory = async function(key, value) {
            const workflowid = self.workflow.id();
            const workflowHistory = {
                workflowid,
                completed: false,
                stepdata: {
                    // Django view will patch in this key, keeping existing keys
                    [ko.unwrap(self.name)]: {
                        [key]: value,
                    },
                },
            };

            fetch(arches.urls.workflow_history + workflowid, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                },
                body: JSON.stringify(workflowHistory),
            });

        };

        // For step locking
        this.getFromLocalStorage = function(key) {
            var allStepsLocalStorageData = JSON.parse(localStorage.getItem(STEPS_LABEL)) || {};

            if (allStepsLocalStorageData[ko.unwrap(self.name)] && typeof allStepsLocalStorageData[ko.unwrap(self.name)][key] !== "undefined") {
                return JSON.parse(allStepsLocalStorageData[ko.unwrap(self.name)][key]);
            }
        };

        this.getItemFromWorkflowHistoryData = async function(key) {
            const workflowData = await self.getWorkflowHistoryData();
            return workflowData?.stepdata?.[key];
        };

        this.getWorkflowHistoryData = async function() {
            const workflowid = self.workflow.id();
            const response = await fetch(arches.urls.workflow_history + workflowid, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    "X-CSRFToken": Cookies.get('csrftoken')
                },
            });
            const data = await response.json(); 
            return data;
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
                });
            }
        };

        this.lockExternalStep = function(step, locked) {
            if (self.lockableExternalSteps.indexOf(step) > -1){
                config.workflow.toggleStepLockedState(step, locked);
            } else {
                throw new Error("The step, " + step + ", cannot be locked");
            }
        };

        this.initialize();
    };

    /* only register template here, params are passed at the workflow level */ 
    ko.components.register('workflow-step', {
        template: workflowStepTemplate,
    });
    
    return WorkflowStep;
});
