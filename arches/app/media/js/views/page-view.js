define([
    'jquery',
    'underscore',
    'backbone',
    'knockout'
], function($, _, Backbone, ko) {
    var PageView = Backbone.View.extend({
        el: $('body'),

        constructor: function (options) {
            var self = this;
            this.viewModel = (options && options.viewModel) ? options.viewModel : {};

            _.defaults(this.viewModel, {
                loading: ko.observable(false),
                showTabs: ko.observable(false),
                tabsActive: ko.observable(false),
                menuActive: ko.observable(false),
                navigate: function(url) {
                    self.viewModel.loading(true);
                    window.location = url;
                }
            });

            Backbone.View.apply(this, arguments);

            ko.applyBindings(this.viewModel);
            return this;
        }
    });
    return PageView;
});
