define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.tile,

        defaults: {
            'tileid': '',
            'data': '',
            'nodegroup_id': '',
            'parenttile_id': '',
            'resourceinstance_id': ''
        }
    });
});