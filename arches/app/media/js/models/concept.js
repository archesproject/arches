define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept,

        defaults: {
            'id': '',
            'label': null,
            'note': null,
            'language': null,
            'parentconceptid': null
        }
    });
});