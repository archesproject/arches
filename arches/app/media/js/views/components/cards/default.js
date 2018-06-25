define(['knockout'], function (ko) {
    var viewModel = function(params) {
        var self = this;
        this.state = params.state || 'form';
        this.loading = params.loading || ko.observable(false);
        this.card = params.card;
        this.tile = params.tile;
        this.form = params.form;
        this.expanded = ko.observable(true);
    };
    return ko.components.register('default-card', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/cards/default.htm' }
    });
});
