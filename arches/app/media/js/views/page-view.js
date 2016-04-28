define([
    'jquery',
    'underscore',
    'backbone',
    'knockout'
], function($, _, Backbone, ko) {
    var PageView = Backbone.View.extend({
        el: $('body'),

        constructor: function (options) {
            this.viewModel = (options && options.viewModel) ? options.viewModel : {};

            _.defaults(this.viewModel, {
                loading: ko.observable(false),
                showTabs: ko.observable(true),
                tabsActive: ko.observable(false)
            });

            Backbone.View.apply(this, arguments);

            ko.applyBindings(this.viewModel);
            return this;
        }
    });
    return PageView;
});
