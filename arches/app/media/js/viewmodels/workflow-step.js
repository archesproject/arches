define([
    'knockout',
    'underscore',
    'knockout-mapping'
], function(ko, _, koMapping) {
    var WorkflowStep = function(config) {
        var self = this;

        this.classUnvisited = 'workflow-step-icon';
        this.classActive = 'workflow-step-icon active';
        this.classComplete = 'workflow-step-icon complete';
        this.classCanAdavance = 'workflow-step-icon can-advance';
        this.icon = 'fa-chevron-circle-right';
        this.title = '';
        this.subtitle = '';
        this.description = '';

        this.informationBoxData = ko.observable();
        if (config.informationboxdata) {
            self.informationBoxData({
                // hidden: self.getInformationBoxHiddenState(),
                hidden: true,
                heading: config.informationboxdata['heading'],
                text: config.informationboxdata['text'],
            })
        }

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

        this.hideInformationBox = function() {
            var informationBoxData = self.informationBoxData();
            informationBoxData['hidden'] = true;

            self.informationBoxData(informationBoxData);

            // set localStorage
        };

        this.showInformationBox = function() {
            var informationBoxData = self.informationBoxData();
            informationBoxData['hidden'] = false;
            
            self.informationBoxData(informationBoxData);

            // set localStorage
        };

        this.getInformationBoxHiddenState = function() {
            // fetch localStorage
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
    };
    return WorkflowStep;
});
