define([
    'knockout',
    'underscore',
    'uuid',
    'arches',
    'views/components/workflows/summary-step',
], function(ko, _, uuid, arches, SummaryStep) {

    function viewModel(params) {
        var self = this;

        params.form.resourceId(params.observationInstanceResourceId);
        SummaryStep.apply(this, [params]);

        this.resourceLoading = ko.observable(true);
        this.digitalResourceLoading = ko.observable(true);
        this.fileLists = ko.observableArray();

        this.tableConfig = {
            "info": false,
            "paging": false,
            "scrollCollapse": true,
            "searching": false,
            "ordering": false,
            "columns": [
                null,
                null,
                null,
            ]
        };

        this.hasAnnotatedParts = Array.isArray(params.uploadedDatasets);
        this.uploadedDatasets = this.hasAnnotatedParts ? params.uploadedDatasets : [params.uploadedDataset];

        this.parentPhysThingData = ko.observableArray();
        this.parentPhysThingRelatedData = ko.observableArray();
        this.parentPhysThingAnnotations = ko.observableArray();

        this.getResourceData(params.parentPhysThingResourceId, this.parentPhysThingData);

        this.parentPhysThingData.subscribe(function(val){
            if (val.resource['Part Identifier Assignment']){
                val.resource['Part Identifier Assignment'].forEach(function(annotation){
                    var annotationName = self.getResourceValue(annotation,['Part Identifier Assignment_Physical Part of Object','@display_value']);
                    var annotationLabel = self.getResourceValue(annotation,['Part Identifier Assignment_Label','@display_value']);
                    var annotator = self.getResourceValue(annotation,['Part Identifier Assignment_Annotator','@display_value']);
                    var tileId = self.getResourceValue(annotation,['@tile_id']);
                    var annotationStr = self.getResourceValue(annotation,['Part Identifier Assignment_Polygon Identifier','@display_value']);
                    if (annotationStr) {
                        var annotationJson = JSON.parse(annotationStr.replaceAll("'",'"'));
                        var leafletConfig = self.prepareAnnotation(annotationJson);
                    }
    
                    self.parentPhysThingAnnotations.push({
                        tileId: tileId,
                        name: annotationName,
                        label: annotationLabel,
                        annotator: annotator,
                        leafletConfig: leafletConfig,
                    });
                });
            };

            this.uploadedDatasets.forEach(function(dataset){
                var selectedDatasetData = ko.observableArray();
                var fileList = ko.observableArray();
                var leafletConfig = ko.observableArray();

                self.parentPhysThingAnnotations().forEach(function(annotation){
                    if (dataset.tileid === annotation.tileId) {
                        leafletConfig = annotation.leafletConfig;
                    }
                });
    
                self.getResourceData(dataset.datasetId, selectedDatasetData);
                selectedDatasetData.subscribe(function(val){
                    var findStatementType= function(statements, type){
                        var foundStatement = _.find(statements, function(statement) {
                            return statement.type.indexOf(type) > -1;
                        });
                        return foundStatement ? foundStatement.statement : "None";
                    };
    
                    var digitalResourceName = val.displayname;
    
                    var files = val.resource?.File.map(function(file){
                        var statements = [];
                        var fileName = self.getResourceValue(file['file_details'][0], ['name']);
                        if (Array.isArray(file["FIle_Statement"])) {
                            statements = file["FIle_Statement"].map(function(statement){
                                return {
                                    statement: self.getResourceValue(statement, ['FIle_Statement_content','@display_value']),                        
                                    type: self.getResourceValue(statement, ['FIle_Statement_type','@display_value'])
                                };
                            });
                        }
                        return {
                            fileName: fileName,
                            statements: statements,
                        };
                    }) || [];
        
                    files.forEach(function(file){
                        var fileName = file.fileName;
                        var fileInterpretation = findStatementType(file.statements, 'interpretation');
                        var fileParameter = findStatementType(file.statements, 'brief text');    
                        fileList.push({
                            name: fileName,
                            interpretation: fileInterpretation,
                            parameter: fileParameter,
                        });
                    });
                    self.fileLists.push({
                        digitalResourceName: digitalResourceName,
                        leafletConfig: leafletConfig,
                        fileList: fileList,
                    });
                });
            });    

            self.digitalResourceLoading(false);
            if (!self.resourceLoading()){
                self.loading(false);
            }
        }, this);
        
        this.resourceData.subscribe(function(val){ //this is the observation resource data
            var findStatementType= function(val, type){
                try {
                    self.reportVals.statements = val.resource['Statement'].map(function(val){
                        return {
                            content:  {'name': 'Instrument Parameters', 'value': self.getResourceValue(val, ['Statement_content','@display_value'])},
                            type: {'name': 'type', 'value': self.getResourceValue(val, ['Statement_type','@display_value'])}
                        };
                    });
                } catch(e) {
                    console.log(e);
                    self.reportVals.statements = [];
                }
                var foundStatement = _.find(self.reportVals.statements, function(statement) {
                    return statement.type.value.split(",").indexOf(type) > -1;
                });
                return foundStatement ? foundStatement.content : {'name': 'Instrument Parameters', 'value': 'None'};
            };
    
            this.displayName = val['displayname'] || 'unnamed';
            this.reportVals = {
                observationName: {'name': 'Experiment/Observation Name', 'value': this.getResourceValue(val.resource['Name'][0], ['Name_content','@display_value'])},
                project: {'name': 'Project', 'value': this.getResourceValue(val.resource, ['part of','@display_value'])},
                usedObject: {'name': 'Used Object', 'value': this.getResourceValue(val.resource, ['observed','@display_value'])},
                usedInstrument: {'name': 'Instrument', 'value': this.getResourceValue(val.resource, ['used instrument','@display_value'])},
                usedProcess: {'name': 'Technique', 'value': this.getResourceValue(val.resource, ['used process','@display_value'])},
            };

            self.reportVals.statement = findStatementType(val, 'description');

            this.resourceLoading(false);
            if (!this.digitalResourceLoading()){
                this.loading(false);
            }
        }, this);
    }

    ko.components.register('upload-dataset-final-step', {
        viewModel: viewModel,
        template: { require: 'text!templates/views/components/workflows/upload-dataset/upload-dataset-final-step.htm' }
    });
    return viewModel;
});
