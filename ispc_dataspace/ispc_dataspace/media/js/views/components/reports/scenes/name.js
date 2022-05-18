define(['underscore', 'knockout', 'arches', 'utils/report','bindings/datatable'], function(_, ko, arches, reportUtils) {
    return ko.components.register('views/components/reports/scenes/name', {
        viewModel: function(params) {
            var self = this;
            Object.assign(self, reportUtils);

            self.nameTableConfig = {
                ...self.defaultTableConfig,
                columns: Array(4).fill(null)
            };

            self.identifierTableConfig = {
                ...self.defaultTableConfig,
                columns: Array(3).fill(null)
            };

            self.dataConfig = {
                name: 'Name',
                identifier: 'Identifier',
                exactMatch: 'exactmatch',
                type: 'type'
            }

            self.cards = Object.assign({}, params.cards);
            self.edit = params.editTile || self.editTile;
            self.delete = params.deleteTile || self.deleteTile;
            self.add = params.addTile || self.addNewTile;
            self.names = ko.observableArray();
            self.identifiers = ko.observableArray();
            self.exactMatch = ko.observableArray();
            self.type = ko.observable();
            self.summary = params.summary || false;
            self.visible = {
                names: ko.observable(true),
                identifiers: ko.observable(true),
                classifications: ko.observable(true)
            }
            Object.assign(self.dataConfig, params.dataConfig || {});

            // if params.compiled is set and true, the user has compiled their own data.  Use as is.
            if(params?.compiled){
                self.names(params.data.names);
                self.identifiers(params.data.identifiers);
                self.exactMatch(params.data.exactMatch);
                self.type(params.data.type);
            } else {
                let nameData = params.data()[self.dataConfig.name];
                if(nameData?.length === undefined){
                    nameData = [nameData]
                } 

                self.names(nameData.map(x => {
                    const type = self.getNodeValue(x, {
                        testPaths: [
                            [`${self.dataConfig.name.toLowerCase()}_type`], 
                            ['type']
                        ]});
                    const content = self.getNodeValue(x, {
                        testPaths: [
                            [`${self.dataConfig.name.toLowerCase()}_content`], 
                            ['content']
                        ]});
                    const language = self.getNodeValue(x, {
                        testPaths: [
                            [`${self.dataConfig.name.toLowerCase()}_language`],
                            ['language']
                        ]});

                    const tileid = self.getTileId(x);
                    return { type, content, language, tileid }
                }));

                let identifierData = params.data()[self.dataConfig.identifier];
                if(identifierData) {
                    if(identifierData.length === undefined){
                        identifierData = [identifierData]
                    } 

                    self.identifiers(identifierData.map(x => {
                        const type = self.getNodeValue(x,{
                            testPaths: [
                                [`${self.dataConfig.identifier.toLowerCase()}_type`], 
                                ['type']
                            ]});
                        const content = self.getNodeValue(x, {
                            testPaths: [
                                [`${self.dataConfig.identifier.toLowerCase()}_content`], 
                                ['content']
                            ]});

                        const tileid = self.getTileId(x);
                        return { type, content, tileid }
                    }));
                }

                let exactMatchData = self.getRawNodeValue(params.data(), self.dataConfig.exactMatch);
                if(exactMatchData) {
                    if(exactMatchData.length === undefined){
                        exactMatchData = [exactMatchData]
                    }
                    self.exactMatch(exactMatchData.map(x => self.getNodeValue(x)))
                }

                self.type(self.getNodeValue(params.data(), self.dataConfig.type));
            } 

        },
        template: { require: 'text!templates/views/components/reports/scenes/name.htm' }
    });
});