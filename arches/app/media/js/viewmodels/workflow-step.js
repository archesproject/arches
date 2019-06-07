define([
    'knockout',
    'underscore',
    'knockout-mapping'
], function(ko, _, koMapping) {
    var WorkflowStep = function(config) {
        this.classUnvisited = 'workflow-step-icon';
        this.classActive = 'workflow-step-icon active';
        this.classComplete = 'workflow-step-icon complete';
        this.icon = 'fa-chevron-circle-right';
        this.title = '';
        this.subtitle = '';
        this.description = '';
        this.complete = ko.observable(false);
        this.active = ko.computed(function() {
            return config.workflow.activeStep() === this;
        }, this);

        this.value = function(){
            return {};
        };

        _.extend(this, koMapping.fromJS(config));

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

        this.ready = ko.observable(false);
        var self = this;

        require([config.component], function(componentViewmodel) {
            self.componentViewmodel = componentViewmodel;
            self.ready(true);
        });
    };
    return WorkflowStep;
});
