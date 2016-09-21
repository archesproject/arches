define([
    'jquery',
    'backbone',
    'knockout',
    'arches',
    'widgets',
    'models/card',
    'resource-editor-data',
], function($, Backbone, ko, arches, widgets, CardModel, data) {
    var FormView = Backbone.View.extend({
        /**
        * A backbone view representing a card form preview
        * @augments Backbone.View
        * @constructor
        * @name FormView
        */

        /**
        * Initializes the view with optional parameters
        * @memberof FormView.prototype
        */
        initialize: function(options) {
            var self = this;
            this.formid = options.formid;
            this.widgetLookup = widgets;
            this.selection = ko.observable();
            this.card = ko.observable(new CardModel({}));
           
            this.currentTabIndex = ko.computed(function () {
                if (!self.card().isContainer()) {
                    return 0;
                }
                var index = self.card().get('cards')().indexOf(self.selection());
                return index;
            });
            this.currentTabCard = ko.computed(function () {
                if(self.card().get('cards')().length === 0){
                    return self.card();
                }else{
                    return self.card().get('cards')()[self.currentTabIndex()];
                }
            }, this)

            this.loadForm(this.formid);
        },

        loadForm: function(formid, callback){
            var self = this;
            $.ajax({
                type: "GET",
                url: arches.urls.resource_data + formid,
                success: function(response) {
                    window.location.hash = formid;
                    self.card(new CardModel({
                        data: response.forms[0].cardgroups[0],
                        datatypes: data.datatypes
                    }));
                    if(self.card().isContainer()){
                        self.selection(self.card().get('cards')()[0]);
                    }else{
                        self.selection(self.card());
                    }
                },
                error: function(response) {

                },
                complete: function(response){
                    if(callback){
                        callback(response)
                    }
                }
            });
        },



    });
    return FormView;
});
