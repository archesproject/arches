define([
    'knockout'
], function(ko) {
    var WorkflowSelect = function() {
        this.workflows = ko.observableArray([
            // {
            //     name: "Application Area",
            //     bgColor: "#87bceb",
            //     circleColor: "#a7cdf0",
            //     icon: "fa-building-o",
            //     desc: "An area that may be re-developed pr newly built"
            // }
        ]);
    };
    return WorkflowSelect;
});
