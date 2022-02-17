define([
    'underscore',
    'backbone',
    'knockout',
    'widgets',
    'card-configuration-data',
    'bindings/ckeditor',
    'knockstrap',
    'component-templates'
], function(_, Backbone,  ko, widgets, data) {
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
            this.graph = options.graphModel;
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

            this.checkIfImmutable = function() {
                var isImmutable = false;
                var card = self.card();
                if (card) {
                    isImmutable = !card.get('is_editable');
                }
                return isImmutable;
            }

            this.toggleRequired = function() {
                    var nodeRequired = this.widget().node.isrequired;
                    var cardEditable = this.card().get('is_editable');
                    if (cardEditable === true) {
                        nodeRequired(!nodeRequired());
                    }
            };

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
        }
    });
    return CardComponentForm;
});
