define([
    'knockout', 'underscore'
], function(ko, _) {
    var WorkflowStep = function(config) {
        this.color = '#543';
        this.icon = 'fa-chevron-circle-right';
        this.title = 'Title';
        this.subtitle = 'Subtitle';
        this.description = 'description of step here';
        this.complete = false;
        this.active = false;

        _.extend(this, config);
    };
    return WorkflowStep;
});