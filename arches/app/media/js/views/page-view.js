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
                showTabs: ko.observable(false),
                tabsActive: ko.observable(false),
                menuActive: ko.observable(true)
            });

            Backbone.View.apply(this, arguments);

            ko.applyBindings(this.viewModel);
            return this;
        }
    });
    return PageView;
});
