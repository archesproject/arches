define(['knockout'], function (ko) {
    var viewModel = function(params) {
        this.card = params.card;
        this.tile = params.tile;
        console.log(params.form);
        this.form = params.form;
        this.formData = null;
        this.expanded = ko.observable(true);
    };
    return ko.components.register('default-card', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/cards/default.htm' }
    });
});
