define(['backbone', 'jquery'], function (Backbone, $) {
    return Backbone.Model.extend({
        read: function (callback, scope) {
            this._doRequest({
                type: "GET",
                data: {
                    'format': 'json'
                },
                url: this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.get('id')),
            }, callback, scope, 'read');
        },

        save: function (callback, scope) {
            this._doRequest({
                type: "POST",
                url: this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.get('id')),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'save');
        },

        delete: function (callback, scope) {
            this._doRequest({
                type: "DELETE",
                url: this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.get('id')),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'delete');
        },

        _doRequest: function (config, callback, scope, eventname) {
            var self = this;
            if (! scope){
                scope = self;
            }
            $.ajax($.extend({
                complete: function (request, status) {
                    if (typeof callback === 'function') {
                        callback.call(scope, request, status, self);
                    }                    
                    if (status === 'success' &&  request.responseJSON) {
                        self.set(request.responseJSON);
                        self.trigger(eventname, self);
                    }
                }
            }, config));
        }
    });
});