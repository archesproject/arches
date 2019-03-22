define([
    'knockout',
], function(ko) {
    var ConstraintViewModel = function(params) {

        this.uniqueToAllInstances = ko.observable(params.uniqueToAllInstances || false);
        this.widgets = params.widgets || [];
        this.nodeIds = ko.observableArray();

        this.getSelect2ConstraintConfig = function(placeholder){
            return {
                clickBubble: true,
                disabled: false,
                data: {results: this.widgets.map(function(c){return {text: c.label(), id: c.node.nodeid};})},
                value: this.nodeIds,
                multiple: params.multiple || true,
                closeOnSelect: false,
                placeholder: placeholder || "Select Widgets",
                allowClear: true
            };
        };

    };

    return ConstraintViewModel;
});
