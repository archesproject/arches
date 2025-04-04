import arches from 'arches';
import AbstractModel from 'models/abstract';

export default AbstractModel.extend({
    url: arches.urls.concept_value,

    defaults: {
        id: '',
        value: '',
        type: '',
        category: '',
        language: '',
        conceptid: ''
    }
});
