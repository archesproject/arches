define([
    'backbone',
    'knockout'
], function(Backbone, ko) {
    var NodeFormView = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.node = ko.observable(null);
            _.extend(this, _.pick(options, 'node'));
        },
        close: function() {
            this.node().editing(false);
        }
    });
    return NodeFormView;
});
