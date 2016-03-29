define([
    'backbone'
], function(Backbone) {
    var NodeFormView = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            this.node = ko.observable(null);
            _.extend(this, _.pick(options, 'node'));
        }
    });
    return NodeFormView;
});
