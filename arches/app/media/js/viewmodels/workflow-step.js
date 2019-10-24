define([
    'knockout',
    'underscore',
    'knockout-mapping'
], function(ko, _, koMapping) {
    var WorkflowStep = function(config) {
        this.classUnvisited = 'workflow-step-icon';
        this.classActive = 'workflow-step-icon active';
        this.classComplete = 'workflow-step-icon complete';
        this.classCanAdavance = 'workflow-step-icon can-advance'
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
        console.log(ko.unwrap(config));

        this.prevStep = function(step){
            self.workflow.previousStep()
        }

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
            console.log(self);
            var ret = '';
            if(this.active()){
                ret = this.classActive;
            }else if(this.complete()){
                ret = this.classComplete;
            } else if(false == true) {
                //.steps[activeStep._index+1]
                ret = this.classCanAdavance;
            }else {
                ret = this.classUnvisited;
            }
            // if one before was not required and not complete, set this class to 'can proceed'
            return ret + ' ' + ko.unwrap(this.icon);
        }, this);
    };
    return WorkflowStep;
});
