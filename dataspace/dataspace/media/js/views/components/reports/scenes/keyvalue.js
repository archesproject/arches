define(['underscore', 'knockout', 'arches', 'utils/report','bindings/datatable'], function(_, ko, arches, reportUtils) {
    return ko.components.register('views/components/reports/scenes/keyvalue', {
        // IMPORTANT:  this scene *requires* you to compile your own data.  Aboutness is too disparate across all models.
        viewModel: function(params) {
            var self = this;
            Object.assign(self, reportUtils);

            self.cards = Object.assign({}, params.cards);
            self.edit = params.editTile || self.editTile;
            self.delete = params.deleteTile || self.deleteTile;
            self.add = params.addTile || self.addNewTile;
            self.item = ko.unwrap(params.data);
            self.visible = {};
            self.inline = params.inline || false;
            self.small = params.small || false;
        },
        template: { require: 'text!templates/views/components/reports/scenes/keyvalue.htm' }
    });
});