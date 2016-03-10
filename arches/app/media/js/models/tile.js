define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.tile,

        defaults: {
            'tileid': '',
            'data': '',
            'nodegroupid': '',
            'parenttileid': '',
            'resourceinstanceid': ''
        }
    });
});