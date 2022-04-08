define(['models/abstract'], function (AbstractModel) {
    const arches = window.arches;

    return AbstractModel.extend({
        url: arches.urls.concept_manage_parents,

        defaults: {
            'id': '',
            'added': [],
            'deleted': []
        }
    });
});
