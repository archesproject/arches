define([
    'knockout', 'underscore'
], function(ko, _) {
    var WorkflowStep = function(config) {
        this.classUnvisited = 'workflow-step-icon';
        this.classActive = 'workflow-step-icon active';
        this.classComplete = 'workflow-step-icon complete';
        this.icon = 'fa-chevron-circle-right';
        this.title = config.title || 'Title';
        this.subtitle = config.subtitle || 'Subtitle';
        this.description = config.description || 'description of step here';
        this.complete = ko.observable(false);
        this.active = ko.observable(false);

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
            return ret + ' ' + this.icon;
        }, this);
    };
    return WorkflowStep;
});
