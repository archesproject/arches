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
        }
    });
});