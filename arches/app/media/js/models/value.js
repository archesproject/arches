define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
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