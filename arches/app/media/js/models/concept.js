define(['arches', 'models/abstract'], function (arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept,

        defaults: {
            'id': '',
            'legacyoid': '',
            'relationshiptype': '',
            'values': [],
            'subconcepts': [],
            'parentconcepts': [],
            'relatedconcepts': []
        },

        reset: function(){
            var conceptid = this.get('id');
            this.clear();
            this.set('id', conceptid);            
        }

    });
});