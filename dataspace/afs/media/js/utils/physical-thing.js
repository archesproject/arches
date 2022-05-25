define([
    'utils/resource'
], function(resourceUtils) {
    return {
        getManifests: function(tiles) {
            return new Promise(function(resolve) {
                var VisualWorkUsedImagenodeid = '9743a1b2-8591-11ea-97eb-acde48001122';
                var DigitalResourceIdentifierContentnodeid = 'db05c421-ca7a-11e9-bd7a-a4d18cec433a';
                var DigitalResourceIdentifierTypenodeid = 'db05c05e-ca7a-11e9-8824-a4d18cec433a';
                var URLConceptvalueid = 'f32d0944-4229-4792-a33c-aadc2b181dc7';
                var ShowsItemId = '2fe9f066-b31e-11e9-b3be-a4d18cec433a';
                var shows = resourceUtils.getNodeValues({
                    nodeId: ShowsItemId,
                    returnTiles: false
                }, tiles);
                if (shows.length === 0) resolve([]);
                shows.forEach(function(relatedResourceItem) {
                    resourceUtils.lookupResourceInstanceData(relatedResourceItem.resourceId)
                        .then(function(data) {
                            var usedimageresourceids = resourceUtils.getNodeValues({
                                nodeId: VisualWorkUsedImagenodeid,
                                returnTiles: false
                            }, data._source.tiles);
                            if (usedimageresourceids.length === 0) resolve([]);
                
                            // look up related Digital Resource
                            usedimageresourceids.forEach(function(relatedResourceItem) {
                                resourceUtils.lookupResourceInstanceData(relatedResourceItem.resourceId)
                                    .then(function(data) {
                                        // console.log(data)
                                        var manifests = resourceUtils.getNodeValues({
                                            nodeId: DigitalResourceIdentifierContentnodeid,
                                            where: {
                                                nodeId: DigitalResourceIdentifierTypenodeid,
                                                contains: URLConceptvalueid
                                            },
                                            returnTiles: false
                                        }, data._source.tiles);
                                        resolve(manifests);
                                    });
                            });
                        });
                });
            });
        }
    };
});
