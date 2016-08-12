define([
    'backbone',
    'knockout',
    'views/graph/card-configuration/permissions-list',
    'widgets',
    'bindings/summernote'
], function(Backbone,  ko, PermissionsList, widgets) {
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
        */
        initialize: function(options) {
            var self = this;
            this.card = options.card;
            this.selection = options.selection || ko.observable(this.card);
            this.helpPreviewActive = options.helpPreviewActive || ko.observable(false);
            this.card = ko.observable();
            this.widget = ko.observable();
            this.widgetLookup = widgets;
            this.widgetList = ko.computed(function() {
                var cardWidget = self.widget();
                if (cardWidget) {
                    var widgets = _.map(self.widgetLookup, function(widget, id) {
                            widget.id = id;
                            return widget;
                        })
                    return _.filter(widgets, function(widget) {
                        return widget.datatype === cardWidget.datatype.datatype
                    })

                } else {
                    return [];
                }
            });

            var widgetUpdating = false;
            this.updateSelection = function(selection) {
                if('isContainer' in selection){
                    this.card(selection);
                }
                if('node' in selection){
                    widgetUpdating = true;
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

            this.widgetId = ko.computed({
                read: function () {
                    return self.widget() ? self.widget().get('widget_id')() : null;
                },
                write: function (value) {
                    if (self.widget() && !widgetUpdating) {
                        self.widget().get('widget_id')(value);
                    }
                    widgetUpdating = false;
                },
                owner: this
            });
        }
    });
    return CardComponentForm;
});
