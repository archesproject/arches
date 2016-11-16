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
            var method = "GET";
            this._doRequest({
                type: method,
                data: {
                    'format': 'json'
                },
                url: this._getURL(method),
            }, callback, scope, 'read');
        },

        /**
         * Posts a model back to the server using the id of the model in the url
         * @memberof AbstractModel.prototype
         * @param  {function} callback - the function to call when the request returns
         * @param  {object} scope - (optional) the scope used for the callback
        */
        save: function (callback, scope) {
            var method = "POST";
            this._doRequest({
                type: method,
                url: this._getURL(method),
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
            var method = "DELETE";
            this._doRequest({
                type: method,
                url: this._getURL(method),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'delete');
        },

        /**
         * Returns the url of the model to use in requests to the server, replaces the placeholder 
         * id 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', if it exists in the url, with the model id, otherwise appends the model id
         * @memberof AbstractModel.prototype
         * @param  {string} method - the type of request being made either "GET", "POST", "DELETE"
        */
        _getURL: function(method){
            var id = this.get('id');
            if(!(id)){
                id = '';
            }
            if(this.url.indexOf('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa') > -1){
                return this.url.replace('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', id);
            }else{
                return this.url + id;
            }
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
                    if (status === 'success') {
                        self.trigger(eventname, self);
                    }
                }
            }, config));
        }
    });
});
