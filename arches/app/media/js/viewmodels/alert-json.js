define(['knockout', 'arches'], function(ko, arches) {
    /**
    * A viewmodel used for alert messages from JSON responses
    *
    * @constructor
    * @name JsonErrorAlertViewModel
    *
    * @param  {string} type - the CSS class name to use to display alert level
    * @param  {object} responseJSON - The response JSON received from the backend
    * @param  {function} cancel (optional) - a function to call on cancel
    * @param  {function} ok (optional) - a function to call on confirmation
    */

    var getPropertyOrDefaultMessage = function(property, defaultMessage) {
        if (typeof property === 'undefined') {
            return defaultMessage;
        }
        else {
            return property;
        }
    };

    var initializeResponseJSON = function(responseJSON) {
        if (typeof responseJSON === 'undefined') {
            responseJSON = {};
        }
        return responseJSON;
    };

    var parseResponseJson = function(responseJSON) {
        responseJSON = initializeResponseJSON(responseJSON);
        responseJSON.title = getPropertyOrDefaultMessage(responseJSON.title, arches.requestFailed.title);
        responseJSON.message = getPropertyOrDefaultMessage(responseJSON.message, arches.requestFailed.text);

        return responseJSON;
    };

    var JsonErrorAlertViewModel = function(type, responseJSON, cancel, ok) {
        var self = this;
        this.active = ko.observable(true);
        this.close = function() {
            self.active(false);
        };

        responseJSON = parseResponseJson(responseJSON);

        this.type = ko.observable(type);
        this.title = ko.observable(responseJSON.title);
        this.text = ko.observable(responseJSON.message);
        this.ok = false;
        this.cancel = false;
        if (typeof ok === 'function') {
            this.ok = function() {
                self.close();
                ok();
            };
        }
        if (typeof cancel === 'function') {
            this.cancel = function() {
                self.close();
                cancel();
            };
        }
    };
    return JsonErrorAlertViewModel;
});
