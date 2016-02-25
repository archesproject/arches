define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.tile,

        defaults: {
            'tileinstanceid': '',
            'tilegroupid': '',
            'tileinstancedata': '',
            'cardid': '',
            'parenttileinstanceid': '',
            'resourceclassid': '',
            'resourceinstanceid': ''
        }
    });
});
