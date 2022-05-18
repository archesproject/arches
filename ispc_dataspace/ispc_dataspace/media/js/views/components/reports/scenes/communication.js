define([
    'knockout', 
    'utils/report',
    'bindings/datatable'
], function(ko, reportUtils) {
    return ko.components.register('views/components/reports/scenes/communication', {
        viewModel: function(params) {
            var self = this;

            Object.assign(self, reportUtils);
            self.map = ko.observable();
            self.selectedAnnotationTileId = ko.observable();
            self.cards = {};
            self.visible = {
                contactPoints: ko.observable(true),
            };

            self.contactPointsTableConfig = {
                ...self.defaultTableConfig,
                columns: Array(3).fill(null)
            };

            self.dataConfig = {
                name: 'contact point',
            };
            self.contactPoints = ko.observableArray();
            self.cards = Object.assign({}, params.cards);

            Object.assign(self.dataConfig, params.dataConfig || {}) 
            if(params?.compiled){
                self.contactPoints(params.data.contactPoints);
            } else {
                self.contactPoints(self.getRawNodeValue(ko.unwrap(params.data), self.dataConfig.name)?.map(
                    x => {
                        const content = self.getNodeValue(x, `${self.dataConfig.name}_content`);
                        const type = self.getNodeValue(x, `${self.dataConfig.name}_type`);
                        const tileid = self.getTileId(x);
                        return { content, type, tileid };
                    }
                ));
            }

        },
        template: {
            require: 'text!templates/views/components/reports/scenes/communication.htm'
        }
    });
});
