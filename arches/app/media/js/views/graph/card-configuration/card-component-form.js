define([
    'underscore',
    'backbone',
    'knockout',
    'views/graph/card-configuration/component-forms/permissions-list',
    'widgets',
    'bindings/summernote',
    'plugins/knockstrap'
], function(_, Backbone,  ko, PermissionsList, widgets) {
    var CardComponentForm = Backbone.View.extend({
        /**
        * A backbone view representing a card component form
        * @augments Backbone.View
        * @constructor
        * @name CardComponentForm
        */

        /**
        * Initializes the view with optional parameters
        * @memberof CardComponentForm.prototype
        * @param {boolean} options.selection - the selected item, either a {@link CardModel} or a {@link NodeModel}
        */
        initialize: function(options) {
            var self = this;
            _.extend(this, _.pick(options, 'card'));
            this.selection = options.selection || ko.observable(this.card);
            this.helpPreviewActive = options.helpPreviewActive || ko.observable(false);
            this.card = ko.observable();
            this.widget = ko.observable();
            this.widgetLookup = widgets;
            this.widgetList = function() {
                var cardWidget = self.widget();
                if (cardWidget) {
                    var widgets = _.map(self.widgetLookup, function(widget, id) {
                        widget.id = id;
                        return widget;
                    });
                    return _.filter(widgets, function(widget) {
                        return widget.datatype === cardWidget.datatype.datatype
                    });
                } else {
                    return [];
                }
            };

            this.validations = ko.computed(function () {
                var functionIDs = [];
                if (self.widget()) {
                    functionIDs = self.widget().datatype.functions;
                }
                return _.filter(options.functions, function(fn) {
                    return (_.contains(functionIDs, fn.functionid) && fn.functiontype !== 'user_selectable');
                })
            });

            this.functions = ko.computed(function () {
                var functionIDs = [];
                if (self.widget()) {
                    functionIDs = self.widget().datatype.functions;
                }
                return _.filter(options.functions, function(fn) {
                    return (_.contains(functionIDs, fn.functionid) && fn.functiontype === 'user_selectable');
                })
            }).extend({ rateLimit: 500 });

            this.cardfunctions = options.functions.filter(function(fn) {
                return fn.functiontype === 'nodegroup';
            });

            this.updateSelection = function(selection) {
                if('isContainer' in selection){
                    this.card(selection);
                }
                if('node' in selection){
                    this.widget(selection);
                }
            };

            this.selection.subscribe(function (selection) {
                this.helpPreviewActive(false);
                this.updateSelection(selection);
            }, this);

            this.updateSelection(this.selection());

            this.permissionsList = new PermissionsList({
                card: this.card,
                permissions: options.permissions
            });
        }
    });
    return CardComponentForm;
});
