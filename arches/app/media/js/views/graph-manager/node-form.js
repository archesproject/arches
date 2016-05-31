define([
    'underscore',
    'backbone',
    'knockout',
    'views/graph-manager/branch-list',
    'bindings/chosen'
], function(_, Backbone, ko, BranchListView) {
    var NodeFormView = Backbone.View.extend({
        /**
        * A backbone model to manage graph data
        * @augments Backbone.View
        * @constructor
        * @name NodeFormView
        */
        initialize: function(options) {
            var self = this;
            _.extend(this, _.pick(options, 'graphModel', 'validations', 'branches'));
            this.datatypes = _.keys(this.graphModel.get('datatypelookup'));
            this.node = this.graphModel.get('selectedNode');
            this.closeClicked = ko.observable(false);
            this.loading = options.loading || ko.observable(false);
            this.failed = ko.observable(false);

            this.branchListView = new BranchListView({
                el: $('#branch-library'),
                branches: ko.observableArray(_.filter(this.branches, function(branch){return branch.isresource === false})),
                graphModel: this.graphModel,
                loading: this.loading
            });

            this.node.subscribe(function () {
                self.closeClicked(false);
            });
        },

        /**
         * closes the node form view
         */
        close: function() {
            this.failed(false);
            this.closeClicked(true);
            if (this.node() && !this.node().dirty()) {
                this.node().selected(false);
            }
        },

        /**
         * resets the edited model and closes the form
         */
        cancel: function () {
            this.node().reset();
            this.close();
        },


        /**
         * calls an async method on the graph model based on the passed in
         * method name and optionally closes the form on success.
         * manages showing loading mask & failure alert
         *
         * @param  {string} methodName - method to call on the graph model
         * @param  {boolean} closeOnSuccess - true to close form on success
         */
        callAsync: function (methodName, closeOnSuccess) {
            var self = this
            this.loading(true);
            this.failed(false);
            this.graphModel[methodName](this.node(), function(response, status){
                var success = (status === 'success');
                self.loading(false);
                self.closeClicked(false);
                self.failed(!success);
                if (success && closeOnSuccess) {
                    self.close();
                }
            });
        },

        /**
         * calls the updateNode method on the graph model for the edited node
         */
        save: function () {
            this.callAsync('updateNode');
        },

        /**
         * calls the deleteNode method on the graph model for the edited node
         */
        deleteNode: function () {
            this.callAsync('deleteNode', true);
        },

        /**
         * calls the toggleIsCollector method on the node model
         */
        toggleIsCollector: function () {
            this.node().toggleIsCollector();
        }
    });
    return NodeFormView;
});
