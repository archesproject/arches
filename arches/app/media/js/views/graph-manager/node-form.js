define([
    'backbone',
    'knockout'
], function(Backbone, ko) {
    var NodeFormView = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.node = ko.observable(null);
            this.closeClicked = ko.observable(false);
            _.extend(this, _.pick(options, 'node'));
            this.node.subscribe(function () {
                self.closeClicked(false);
            })
        },
        close: function() {
            this.closeClicked(true);
            if (!this.node().dirty()) {
                this.node().editing(false);
            }
        },
        cancel: function () {
            this.node().reset();
            this.close();
        }
    });
    return NodeFormView;
});
