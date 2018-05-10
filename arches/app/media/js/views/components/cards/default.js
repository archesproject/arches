define([
    'knockout',
    'knockout-mapping'
], function (ko, koMapping) {
    var viewModel = function(params) {
        this.card = params.card;
        this.tile = params.tile ? params.tile : {
            parent: params.card,
            expanded: ko.observable(true),
            data: koMapping.fromJS(
                _.reduce(this.card.widgets, function (data, widget) {
                    data[widget.node_id] = null;
                    return data;
                }, {})
            ),
            formData: new FormData()
        };
        this.form = params.form;
        this.expanded = ko.observable(true);
    };
    return ko.components.register('default-card', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/cards/default.htm' }
    });
});
