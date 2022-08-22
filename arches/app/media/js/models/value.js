define(['arches', 'models/abstract'], function(arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept_value,
        
        defaults: {
            'id': '',
            'value': '',            
            'type': '',
            'category': '',
            'language': '',
            'conceptid': ''
        }  
    });
});