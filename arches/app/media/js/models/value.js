define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept_value,

        defaults: {
            'value': '',
            'id': null,
            'type': null,
            'datatype': 'text',
            'language': null,
            'conceptid': ''
        }
    });
});