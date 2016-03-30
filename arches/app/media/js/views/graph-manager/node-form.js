define([
    'backbone',
    'knockout'
], function(Backbone, ko) {
    var NodeFormView = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.node = ko.observable(null);
            this.closeClicked = ko.observable(false);
            this.loading = ko.observable(false);
            this.failed = ko.observable(false);

            _.extend(this, _.pick(options, 'node'));

            this.node.subscribe(function () {
                self.closeClicked(false);
            })
        },
        close: function() {
            this.failed(false);
            this.closeClicked(true);
            if (this.node() && !this.node().dirty()) {
                this.node().editing(false);
            }
        },
        cancel: function () {
            this.node().reset();
            this.close();
        },
        callAsync: function (methodName) {
            var self = this
            self.loading(true);
            self.failed(false);
            self.node()[methodName](function (success) {
                self.loading(false);
                self.closeClicked(false);
                self.failed(!success);
                if (success) {
                    self.close();
                }
            });
        },
        save: function () {
            this.callAsync('save');
        },
        remove: function () {
            this.callAsync('remove');
        }
    });
    return NodeFormView;
});
