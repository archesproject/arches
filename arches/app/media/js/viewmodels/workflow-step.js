import ko from 'knockout';
import _ from 'underscore';
import koMapping from 'knockout-mapping';
import arches from 'arches';
import uuid from 'uuid';
import Cookies from 'js-cookie';
import WorkflowComponentAbstract from 'views/components/workflows/workflow-component-abstract';
import workflowStepTemplate from 'templates/views/components/plugins/workflow-step.htm';


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
        const components = Object.values(self.workflowComponentAbstractLookup());
        if (!components.length) {
            // New workflow being initialized.
            return false;
        }
        return components.every(component => component.complete());
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
        // The componentIdLookup will be a noop, but we need to post the "locked" info
        self.setToWorkflowHistory(COMPONENT_ID_LOOKUP_LABEL, self.componentIdLookup());
    });

    this.initialize = function() {
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
        if (config.workflowHistory.stepdata) {
            const stepData = config.workflowHistory.stepdata[ko.unwrap(self.name)];
            self.componentIdLookup(stepData?.[COMPONENT_ID_LOOKUP_LABEL]);
            self.locked(stepData?.locked);
        }

        /* cached informationBox logic */
        this.setupInformationBox();

        /* build page layout */ 
        ko.toJS(self.layoutSections).forEach(function(layoutSection) {
            var uniqueInstanceNames = [];

            layoutSection.componentConfigs.forEach(function(componentConfigData) {
                uniqueInstanceNames.push(componentConfigData.uniqueInstanceName);
                self.updateWorkflowComponentAbstractLookup(componentConfigData);
            });

            self.pageLayout.push([layoutSection.sectionTitle, uniqueInstanceNames]);
        });

        /* assigns componentIdLookup to self, which updates workflow history */
        var componentIdLookup = Object.keys(self.workflowComponentAbstractLookup()).reduce(function(acc, key) {
            acc[key] = self.workflowComponentAbstractLookup()[key].id();
            return acc;
        }, {});

        self.componentIdLookup(componentIdLookup);
    };

    this.updateWorkflowComponentAbstractLookup = function(workflowComponentAbtractData) {
        var workflowComponentAbstractLookup = self.workflowComponentAbstractLookup();
        var workflowComponentAbstractId = null;

        if (config.workflowHistory.stepdata) {
            const componentIdLookup = config.workflowHistory.stepdata?.[ko.unwrap(self.name)]?.[COMPONENT_ID_LOOKUP_LABEL];
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
            workflowName: self.workflow.plugin.componentname,
            alert: self.alert,
            outerSaveOnQuit: self.outerSaveOnQuit,
            isStepActive: self.active,
            workflowHistory: config.workflowHistory,
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

    this.setToWorkflowHistory = function(key, value) {
        const workflowid = self.workflow.id();
        const workflowHistory = {
            workflowid,
            workflowname: self.workflow.plugin.componentname,
            completed: false,
            stepdata: {
                // Django view will patch in this key, keeping existing keys
                [ko.unwrap(self.name)]: {
                    [key]: value,
                    locked: self.locked(),
                    stepId: self.id(),
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

export default WorkflowStep;
