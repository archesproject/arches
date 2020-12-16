const { param } = require("jquery");

define([
    'knockout',
    'underscore',
    'knockout-mapping',
    'uuid'
], function(ko, _, koMapping, uuid) {
    var WorkflowStep = function(config) {
        this.id = ko.observable(config.id || uuid.generate());
        this.workflowId = ko.observable(config.workflow ? config.workflow.id : null);

        // if (this.workflowId()) {
        //     /* let's add the step.id to the workflow's localStorage if not already there */ 
        //     var workflowStepIds = localStorage.getItem(`workflow-${this.workflowId()}`);
            
        //     if (
        //         workflowStepIds
        //         && !workflowStepIds.some(function(workflowStepId) { return workflowStepId !== this.id })
        //     ) {
                
        //     }
        // }

        this.classUnvisited = 'workflow-step-icon';
        this.classActive = 'workflow-step-icon active';
        this.classComplete = 'workflow-step-icon complete';
        this.classCanAdavance = 'workflow-step-icon can-advance';

        this.icon = 'fa-chevron-circle-right';
        this.title = '';
        this.subtitle = '';
        this.description = '';
        
        this.complete = ko.observable(false);
        this.required = ko.observable(ko.unwrap(config.required));
        this.autoAdvance = ko.observable(true);

        this.active = ko.computed(function() {
            return config.workflow.activeStep() === this;
        }, this);

        this.value = function(){
            return {};
        };

        Object.keys(config).forEach(function(prop){
            if(prop !== 'workflow') {
                config[prop] = koMapping.fromJS(config[prop]);
            }
        });

        _.extend(this, config);

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
    };
    return WorkflowStep;
});
