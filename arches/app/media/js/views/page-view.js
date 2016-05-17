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
                dirty: ko.observable(false),
                showConfirmNav: ko.observable(false),
                navDestination: ko.observable(''),
                navigate: function(url, bypass) {
                    if (!bypass && self.viewModel.dirty()) {
                        self.viewModel.navDestination(url);
                        self.viewModel.showConfirmNav(true);
                        return;
                    }
                    self.viewModel.showConfirmNav(false);
                    self.viewModel.loading(true);
                    window.location = url;
                }
            });

            this.viewModel.showConfirmNav.subscribe(function(val) {
                $('#confirm-nav-modal').modal(val?'show':'hide')
            });

            Backbone.View.apply(this, arguments);
            return this;
        },

        initialize: function(options) {
            ko.applyBindings(this.viewModel);
        }
    });
    return PageView;
});
