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
            _.extend(this, _.pick(options, 'card', 'validations', 'functions'));
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
                    });
                    return _.filter(widgets, function(widget) {
                        return widget.datatype === cardWidget.datatype.datatype
                    });
                } else {
                    return [];
                }
            });

            this.updateSelection = function(selection) {
                if('isContainer' in selection){
                    this.card(selection);
                }
                if('node' in selection){
                    // first set this.widget to null before updating, this
                    // prevents the chosen binding from updating this.widgetId
                    // (value) when this.widgetList (options) is updated.
                    //
                    // by setting this.widget to null, we remove the chosen
                    // elements from the DOM entirely and force them to be
                    // rebuilt each time the selection changes.
                    this.widget(null);
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
                    if (self.widget()) {
                        self.widget().get('widget_id')(value);
                    }
                },
                owner: this
            });
        }
    });
    return CardComponentForm;
});
