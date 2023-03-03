define(['arches', 'models/abstract'], function(arches, AbstractModel) {
    return AbstractModel.extend({
        url: arches.urls.concept,

        defaults: {
            'id': '',
            'legacyoid': '',
            'nodetype': '',
            'relationshiptype': '',
            'values': [],
            'subconcepts': [],
            'parentconcepts': [],
            'relatedconcepts': []
        },

        reset: function(){
            var id = this.get('id');
            var legacyoid = this.get('legacyoid');
            var nodetype = this.get('nodetype');
            this.clear();
            this.set('id', id);  
            this.set('legacyoid', legacyoid);  
            this.set('nodetype', nodetype);            
        },

        makeCollection: function(callback, scope){
            return this._doRequest({
                type: 'GET',
                url: arches.urls.concept_make_collection.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.get('id')),
                data: {}
            }, callback, scope, 'collection_created'); 
        },    

    });
});