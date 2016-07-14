define(['backbone', 'jquery'], function (Backbone, $) {
    return Backbone.Model.extend({
        /**
         * A backbone model to manage RESTful requests on a per model basis
         * @constructor
         * @name AbstractModel
        */

        /**
         * Issues a request for a model instance from the server using the id of the model in the url
         * @memberof AbstractModel.prototype
         * @param  {function} callback - the function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
        */
        read: function (callback, scope) {
            this._doRequest({
                type: "GET",
                data: {
                    'format': 'json'
                },
                url: this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.get('id')),
            }, callback, scope, 'read');
        },

        /**
         * Posts a model back to the server using the id of the model in the url
         * @memberof AbstractModel.prototype
         * @param  {function} callback - the function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
        */
        save: function (callback, scope) {
            this._doRequest({
                type: "POST",
                url: this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.get('id')),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'save');
        },

        /**
         * Sends a delete request to the server using the id of the model in the url
         * @memberof AbstractModel.prototype
         * @param  {function} callback - the function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
        */
        delete: function (callback, scope) {
            this._doRequest({
                type: "DELETE",
                url: this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', this.get('id')),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'delete');
        },

        /**
         * _doRequest - a wrapper around a simple ajax call
         * @memberof AbstractModel.prototype
         * @param  {object} config - a config object to pass to the ajax request
         * @param  {function} callback - function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
         * @param  {string} eventname - (optional) the event to trigger upon successfull return of the request
         */
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
