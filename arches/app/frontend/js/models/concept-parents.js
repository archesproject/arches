define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept_manage_parents,

        defaults: {
            'id': '',
            'added': [],
            'deleted': []
        }
    });
});
