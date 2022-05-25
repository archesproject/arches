define([
    'knockout',
    'utils/resource',
    'viewmodels/card',
], function(ko, resourceUtils) {
    
    function viewModel(params) {
        var self = this;
        var componentParams = params.form.componentData.parameters;
        this.physThingSetNodegroupId = 'cc5d6df3-d477-11e9-9f59-a4d18cec433a';
        this.physThingTypeNodeId = '8ddfe3ab-b31d-11e9-aff0-a4d18cec433a';
        this.physicalThingPartOfSetNodeId = '63e49254-c444-11e9-afbe-a4d18cec433a';
        this.partNodeGroupId = 'fec59582-8593-11ea-97eb-acde48001122';
        this.partManifestNodeId = '97c30c42-8594-11ea-97eb-acde48001122';
        this.manifestConcepts = [
            '1497d15a-1c3b-4ee9-a259-846bbab012ed', 
            '00d5a7a6-ff2f-4c44-ac85-7a8ab1a6fb70',
            '305c62f0-7e3d-4d52-a210-b451491e6100'
        ]
        this.digitalReferenceTypeNodeId = 'f11e4d60-8d59-11eb-a9c4-faffc265b501';
        this.digitalReferenceNodeGroupId = '8a4ad932-8d59-11eb-a9c4-faffc265b501';
        this.save = params.form.save;
        this.physicalThingGraphId = componentParams.graphids[0];
        this.projectGraphId = componentParams.graphids[1];
        this.validateThing = componentParams.validateThing;
        this.projectValue = ko.observable();
        this.projectNameValue = ko.observable();
        this.physicalThingValue = ko.observable();
        this.setsThatBelongToTheProject = ko.observable();
        this.hasSetWithPhysicalThing = ko.observable();
        this.isPhysicalThingValid = ko.observable();
        this.originalValue = params.form.value();
        
        this.updateValues = function(val){
            if (val !== null) {
                self.physicalThingValue(val.physicalThing);
                self.setsThatBelongToTheProject(val.physicalThingSet);
                self.projectValue(val.project);
            }
        };

        // update with saved values
        if (params.value()) { 
            this.updateValues(params.value());
        }

        this.locked = params.form.locked;
        
        this.projectValue.subscribe(function(val){
            self.isPhysicalThingValid(null);
            self.physicalThingValue(null);
            if (val) {
                var res = resourceUtils.lookupResourceInstanceData(val);
                res.then(
                    function(data){
                        self.projectNameValue(data._source.displayname);
                        let setTileResourceInstanceIds;
                        let setTile = data._source.tiles.find(function(tile){
                            return tile.nodegroup_id === self.physThingSetNodegroupId;
                        });
                        if (setTile && Object.keys(setTile.data).includes(self.physThingSetNodegroupId) && setTile.data[self.physThingSetNodegroupId].length) {
                            self.setsThatBelongToTheProject(null);
                            setTileResourceInstanceIds = setTile.data[self.physThingSetNodegroupId].map((instance) => instance.resourceId);
                            if (setTileResourceInstanceIds) {
                                self.setsThatBelongToTheProject(setTileResourceInstanceIds);
                            }
                            self.physicalThingValue(null);
                        } else {
                            self.hasSetWithPhysicalThing(false);
                        }
                    }
                );
            }
        });

        this.termFilter = ko.pureComputed(function(){
            if (ko.unwrap(self.setsThatBelongToTheProject)) {
                self.hasSetWithPhysicalThing(true);
                var query = {"op": "and"};
                query[self.physicalThingPartOfSetNodeId] = {
                    "op": "or",
                    "val":  ko.unwrap(self.setsThatBelongToTheProject)
                };
                return function(term, queryString) {
                    queryString.set('advanced-search', JSON.stringify([query]));
                    if (term) {
                        queryString.set('term-filter', JSON.stringify([{"context":"", "id": term,"text": term,"type":"term","value": term,"inverted":false}]));
                    }
                };
            } else {
                return null;
            }
        });

        this.physicalThingValue.subscribe(async (val) => {
            // if the physical thing value isn't set correctly, return step value
            // to original value
            if (!val) { 
                params.value(self.originalValue); 
                return; 
            }
            const physThing = (await resourceUtils.lookupResourceInstanceData(val))?._source;
            
            const digitalReferencesWithManifest = physThing.tiles.
                filter(x => x.nodegroup_id == self.digitalReferenceNodeGroupId &&
                    self.manifestConcepts.includes(x?.data?.[self.digitalReferenceTypeNodeId]));
            const partsWithManifests = physThing.tiles.filter(x => 
                x.nodegroup_id == self.partNodeGroupId &&
                x.data?.[self.partManifestNodeId]?.features?.[0]?.properties?.manifest)

            // Below in defining the 'projectSet' we make sure that we know the collection that the physical thing came from.
            // We need this in order to place child things in the same collection.
            // It remains possible that if the selected physical thing belongs to two different collections
            // within the same selected project we cannot know in which collection we should put it's samples/analysis areas.
            // In this case we are defaulting to the first collection in the project's list of collections that contains the physical thing.
            const setsThatBelongToTheSelectedThing = physThing.tiles.find(x => x.nodegroup_id === self.physicalThingPartOfSetNodeId)?.data[self.physicalThingPartOfSetNodeId].map(y => y.resourceId);
            const projectSet = setsThatBelongToTheSelectedThing.find(setid => self.setsThatBelongToTheProject().includes(setid))

            const analysisAreaValueId = '31d97bdd-f10f-4a26-958c-69cb5ab69af1';
            const sampleAreaValueId = '7375a6fb-0bfb-4bcf-81a3-6180cdd26123';
            const isArea = physThing.tiles.filter(x =>
                x.nodegroup_id == self.physThingTypeNodeId &&
                (x.data?.[self.physThingTypeNodeId].includes(analysisAreaValueId) ||
                x.data?.[self.physThingTypeNodeId].includes(sampleAreaValueId))
            ).length > 0;

            let canNonDestructiveObservation = false;
            let canDestructiveObservation = false;
            if (params.datasetRoute) {
                canNonDestructiveObservation = (params.datasetRoute == 'non-destructive' && digitalReferencesWithManifest.length && partsWithManifests.length)
                canDestructiveObservation= (params.datasetRoute == 'destructive' && !isArea)
            }

            if(!self.validateThing || canNonDestructiveObservation || canDestructiveObservation){
                params.value({
                    physThingName: physThing.displayname,
                    physicalThing: val,
                    projectSet: projectSet,
                    physicalThingSet: self.setsThatBelongToTheProject(),
                    project: self.projectValue(),
                    projectName: self.projectNameValue(),
                });
                self.isPhysicalThingValid(true);
            } else {
                self.isPhysicalThingValid(false);
            }
        });
        
    }

    ko.components.register('select-phys-thing-step', {
        viewModel: viewModel,
        template: {
            require: 'text!templates/views/components/workflows/select-phys-thing-step.htm'
        }
    });

    return viewModel;
});
