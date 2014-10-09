define(['jquery', 'backbone', 'arches'], function ($, Backbone, arches) {
    return Backbone.Model.extend({
        defaults: {
            'value': '',
            'id': null,
            'valuetype': null,
            'datatype': 'text',
            'language': null,
            'conceptid': ''
        },

        save: function(callback) {
            $.ajax({
                type: "POST",
                url: arches.urls.concept_value,
                data: {
                    'json': JSON.stringify(this.toJSON())
                },
                complete: callback
            });
        },
        
        delete: function(callback) {
            $.ajax({
                type: "DELETE",
                url: arches.urls.concept_value + this.get('id'),
                complete: callback
            });
        }
    });
});
