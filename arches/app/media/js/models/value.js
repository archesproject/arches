define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept_value,

        defaults: {
            'value': '',
            'id': null,
            'valuetype': null,
            'datatype': 'text',
            'language': null,
            'conceptid': ''
        }
    });
});