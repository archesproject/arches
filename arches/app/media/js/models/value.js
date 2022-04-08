define(['models/abstract'], function (AbstractModel) {
    const arches = window.arches;

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