define(['backbone', 'arches'], function (Backbone, arches) {
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
                complete: callback
            });
        },

        delete: function (callback) {
            $.ajax({
                type: "DELETE",
                url: arches.urls.concept + this.get('id'),
                complete: callback
            });
        }
    });
});