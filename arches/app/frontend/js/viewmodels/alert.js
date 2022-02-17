define(['knockout'], function (ko) {
    /**
    * A viewmodel used for generic alert messages
    *
    * @constructor
    * @name AlertViewModel
    *
    * @param  {string} type - the CSS class name to use to display alert level
    * @param  {string} title - the alert's title text
    * @param  {string} text - the alert's body text
    * @param  {function} cancel (optional) - a function to call on cancel
    * @param  {function} ok (optional) - a function to call on confirmation
    */
    var AlertViewModel = function(type, title, text, cancel, ok) {
        var self = this;
        this.active = ko.observable(true);
        this.close = function () {
            self.active(false);
        };

        this.type = ko.observable(type);
        this.title = ko.observable(title);
        this.text = ko.observable(text);
        this.ok = false;
        this.cancel = false;
        if (typeof ok === 'function') {
            this.ok = function() {
                self.close();
                ok();
            }
        }
        if (typeof cancel === 'function') {
            this.cancel = function() {
                self.close();
                cancel();
            }
        }
    };
    return AlertViewModel;
});
