define([
    'jquery',
    'underscore',
    'backbone',
    'knockout',
    'bootstrap-nifty'
], function($, _, Backbone, ko) {
    /**
    * A backbone view representing a basic page in arches.  It sets up the
    * viewModel defaults, optionally accepts additional view model data and
    * binds the view model to the entire page.  When using, no other views
    * should bind data to the DOM.
    *
    * @augments Backbone.View
    * @constructor
    * @name PageView
    */
    var PageView = Backbone.View.extend({
        el: $('body'),

        /**
        * Creates an instance of PageView, optionally using a passed in view
        * model
        *
        * @memberof PageView.prototype
        * @param {object} options
        * @param {object} options.viewModel - an optional view model to be
        *                 bound to the page
        * @return {object} an instance of PageView
        */
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
            $('[data-toggle="tooltip"]').tooltip();
        }
    });
    return PageView;
});
