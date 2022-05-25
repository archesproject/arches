define(['underscore', 'knockout', 'arches', 'utils/report','bindings/datatable'], function(_, ko, arches, reportUtils) {
    return ko.components.register('views/components/reports/scenes/documentation', {
        viewModel: function(params) {
            var self = this;
            Object.assign(self, reportUtils);

            self.digitalReferenceTableConfig = {
                ...self.defaultTableConfig,
                columns: Array(3).fill(null)
            };

            self.subjectOfTableConfig = {
                ...self.defaultTableConfig,
                columns: Array(1).fill(null)
            };

            self.dataConfig = {
                label: '_label',
                digitalReference: 'Digital Reference',
                subjectOf: 'subject of'
            }

            self.cards = Object.assign({}, params.cards);
            self.edit = params.editTile || self.editTile;
            self.delete = params.deleteTile || self.deleteTile;
            self.add = params.addTile || self.addNewTile;
            self.digitalReference = ko.observableArray();
            self.label = ko.observable();
            self.subjectOf = ko.observableArray();
            self.visible = {
                digitalReference: ko.observable(true),
                subjectOf: ko.observable(true),
                label: ko.observable(true)
            }
            self.subjectOfDisplay = ko.observable(true);
            self.digitalReferenceDisplay = ko.observable(true)
            Object.assign(self.dataConfig, params.dataConfig || {});

            if(!self.dataConfig.digitalReference){
                self.toggleVisibility(self.digitalReferenceDisplay);
            }
            if(!self.dataConfig.subjectOf) {
                self.toggleVisibility(self.subjectOfDisplay);
            }

            // if params.compiled is set and true, the user has compiled their own data.  Use as is.
            if(params?.compiled){
                self.label(params.data.label);
                self.digitalReference(params.data.digitalReference);
                self.subjectOf(params.data.subjectOf);
            } else {
                if(self.dataConfig.label) {
                    self.label(self.getNodeValue(params.data(), self.dataConfig.label));
                }
                
                if(self.dataConfig.digitalReference){
                    let digitalReferenceData = params.data()[self.dataConfig.digitalReference];
                    if(digitalReferenceData) {
                        if(digitalReferenceData.length === undefined){
                            digitalReferenceData = [digitalReferenceData];
                        } 

                        self.digitalReference(digitalReferenceData.map(x => {
                            const type = self.getNodeValue(x, {
                                testPaths: [
                                    ["digital reference_digital reference type"], 
                                    ["digital reference type"]
                                ]});
                            const source = self.getNodeValue(x, {
                                testPaths: [
                                    ["digital reference_digital source"], 
                                    ["digital source"]
                                ]});
                            const link = self.getResourceLink(self.getRawNodeValue(x, {
                                testPaths: [
                                    ["digital reference_digital source"], 
                                    ["digital source"]
                                ]}));
                            const tileid = x?.['@tile_id'];
                            return { link, type, source, tileid };
                        }));
                    }
                }

                if(self.dataConfig.subjectOf) {
                    const subjectOf = self.getRawNodeValue(params.data(), self.dataConfig.subjectOf);
                    if(subjectOf){
                        const tileid = subjectOf?.['@tile_id'];
                        self.subjectOf(subjectOf?.instance_details.map(x => {
                            const display = x?.display_value;
                            const link = self.getResourceLink(x);
                            return { display, link, tileid }
                        }));
                    }
                }

            } 

        },
        template: { require: 'text!templates/views/components/reports/scenes/documentation.htm' }
    });
});