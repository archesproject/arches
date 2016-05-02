define([
    'underscore',
    'backbone',
    'knockout',
    'bindings/chosen'
], function(_, Backbone, ko) {
    var NodeFormView = Backbone.View.extend({
        initialize: function(options) {
            var self = this;
            _.extend(this, _.pick(options, 'graphModel', 'validations', 'branchListView'));
            this.datatypes = _.keys(this.graphModel.get('datatypelookup'));
            this.node = this.graphModel.get('editNode');
            this.closeClicked = ko.observable(false);
            this.loading = ko.observable(false);
            this.failed = ko.observable(false);

            this.title = ko.computed(function () {
                var node = self.node();
                if (!node || !node.name()) {
                    return '';
                }
                title = node.name();
                if (title.length > 16) {
                    return title.substring(0,16) + '...';
                }
                return title;
            });

            this.node.subscribe(function () {
                self.closeClicked(false);
            });
        },
        close: function() {
            this.failed(false);
            this.closeClicked(true);
            if (this.node() && !this.node().dirty()) {
                this.node().editing(false);
            }
        },
        cancel: function () {
            this.node().reset();
            this.close();
        },
        callAsync: function (methodName, onSuccess) {
            var self = this
            self.loading(true);
            self.failed(false);
            self.node()[methodName](function (request, status) {
                var success = (status === 'success');
                self.loading(false);
                self.closeClicked(false);
                self.failed(!success);
                if (success) {
                    if (onSuccess) {
                        onSuccess(request);
                    }
                    self.close();
                }
            }, self.node());
        },
        save: function () {
            var self = this;
            this.callAsync('save', function (request) {
                var groupNodes = request.responseJSON.group_nodes;
                var nodes = self.graphModel.get('nodes')();
                var nodeJSON = request.responseJSON.node;
                nodeJSON.cardinality = request.responseJSON.nodegroup?request.responseJSON.nodegroup.cardinality:self.node().cardinality();
                self.node().parse(nodeJSON);
                groupNodes.forEach(function(nodeJSON) {
                    var node = _.find(nodes, function (node) {
                        return node.nodeid === nodeJSON.nodeid;
                    });
                    nodeJSON.cardinality = node.cardinality();
                    node.parse(nodeJSON);
                });
            });
        },
        deleteNode: function () {
            var self = this;
            this.callAsync('delete', function () {
                self.graphModel.deleteNode(self.node())
            });
        },
        toggleIsCollector: function () {
            this.node().toggleIsCollector();
        },
        toggleCardinality: function () {
            this.node().toggleCardinality();
        },
        toggleIsResource: function () {
            this.node().isresource(!this.node().isresource());
        },
        toggleIsActive: function () {
            this.node().isactive(!this.node().isactive());
        }
    });
    return NodeFormView;
});
