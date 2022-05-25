define(['arches', 'uuid', 'utils/resource'], function(arches, uuid, ResourceUtils) {
    return {
        saveThingToProject: async function(physicalThingInstanceId, projectSetInstanceId, workflowId, resourceLookup){
            let thing;
            let tileId = "";
            let alreadySaved = false;
            const memberOfSetNodeid = '63e49254-c444-11e9-afbe-a4d18cec433a';
            const data = {};

            data[memberOfSetNodeid] = [{
                "resourceId": projectSetInstanceId,
                "ontologyProperty": "",
                "resourceXresourceId": "",
                "inverseOntologyProperty": ""
            }];

            if (resourceLookup[physicalThingInstanceId]) {
                thing = resourceLookup[physicalThingInstanceId];
            } else {
                thing = await ResourceUtils.lookupResourceInstanceData(physicalThingInstanceId, false);
            }

            const tile = thing._source.tiles.find((tile) => {
                return tile.nodegroup_id === memberOfSetNodeid;
            });

            if (tile) {
                // check if the tile already has a relationship to the current project's collection
                if (tile.data[memberOfSetNodeid].find(val => val.resourceId === projectSetInstanceId)) {
                    alreadySaved = true;
                } else {
                    // if not, add the new collection relationship to existing relationships
                    tileId = tile.tileid;
                    if (Array.isArray(tile.data[memberOfSetNodeid])) {
                        data[memberOfSetNodeid] = data[memberOfSetNodeid].concat(tile.data[memberOfSetNodeid]);
                    }
                }
            }

            const tileObj = {
                "tileid": tileId,
                "data": data,
                "nodegroup_id": memberOfSetNodeid,
                "parenttile_id": null,
                "resourceinstance_id": physicalThingInstanceId,
                "sortorder": 0,
                "tiles": {},
                "transaction_id": workflowId
            };

            if (!alreadySaved) {
                return window.fetch(arches.urls.api_tiles(tileId || uuid.generate()), {
                    method: 'POST',
                    credentials: 'include',
                    body: JSON.stringify(tileObj),
                    headers: {
                        'Content-Type': 'application/json'
                    },
                });
            } else {
                return Promise.resolve();
            }
        },
    };
});