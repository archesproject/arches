import arches from 'arches';
import AbstractModel from 'models/abstract';

export default AbstractModel.extend({
    url: arches.urls.concept_manage_parents,

    defaults: {
        'id': '',
        'added': [],
        'deleted': []
    }
});
