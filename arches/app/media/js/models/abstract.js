define(['backbone', 'jquery'], function (Backbone, $) {
    return Backbone.Model.extend({
        read: function (callback) {
            this._doRequest({
                type: "GET",
                data: {
                    'format': 'json'
                },
                url: this.url + this.get('id')
            }, callback);
        },

        save: function (callback) {
            this._doRequest({
                type: "POST",
                url: this.url,
                data: JSON.stringify(this.toJSON())
            }, callback);
        },

        delete: function (callback) {
            this._doRequest({
                type: "DELETE",
                url: this.url + this.get('id')
            }, callback);
        },

        _doRequest: function (config, callback) {
            var self = this;
            $.ajax($.extend({
                complete: function (request, status) {
                    if (status === 'success' &&  request.responseJSON) {
                        self.set(request.responseJSON);
                    }
                    callback(request, status, self);
                }
            }, config));
        }
    });
});