define(['backbone'], function (Backbone) {
    return Backbone.Model.extend({
        defaults: {
            'id': '',
            'label': null,
            'note': null,
            'language': null,
            'parentconceptid': null,
        },
        
        save: function (callback) {
            $.ajax({
                type: "POST",
                url: arches.urls.concept,
                data: JSON.stringify(this.toJSON()),
                callback: callback
            });
        },

        delete: function (callback) {
            $.ajax({
                type: "DELETE",
                url: arches.urls.concept + this.get('id'),
                callback: callback
            });
        }
    });
});