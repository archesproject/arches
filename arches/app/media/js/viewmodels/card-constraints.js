define([
    'knockout',
], function(ko) {
    var ConstraintViewModel = function(params) {

        this.uniqueToAllInstances = ko.observable(params.uniquetoallinstances || false);
        this.widgets = params.widgets || [];
        this.nodeIds = ko.observableArray(params.nodes);
        this.cardid = params.card_id;
        this.constraintid = params.constraintid;
        this.getSelect2ConstraintConfig = function(placeholder){
            var nodeOptions = this.widgets.map(function(c){return {text: c.label(), id: c.node.nodeid};});
            return {
                clickBubble: true,
                disabled: false,
                data: {results: nodeOptions},
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
