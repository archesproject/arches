define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept_value,

        defaults: {
            'id': null,
            'value': '',            
            'type': null,
            'category': '',
            'datatype': 'text',
            'language': null,
            'conceptid': ''
        }  
    });
});