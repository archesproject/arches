define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        defaults: {
            'id': '',
            'value': '',            
            'type': '',
            'category': '',
            'datatype': 'text',
            'language': '',
            'conceptid': ''
        }  
    });
});