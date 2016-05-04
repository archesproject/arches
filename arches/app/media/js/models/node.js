define([
    'knockout',
    'models/abstract',
    'arches'
], function (ko, AbstractModel, arches) {
    return AbstractModel.extend({
        url: arches.urls.node,

        initialize: function (options) {
            var self = this;
            self.datatypelookup = options.datatypelookup;

            self._node = ko.observable('');
            self.selected = ko.observable(false);
            self.filtered = ko.observable(false);
            self.name = ko.observable('');
            self.nodeGroupId = ko.observable('');
            self.datatype = ko.observable('');
            self.cardinality = ko.observable('n');
            self.validations = ko.observableArray();
            self.isresource = ko.observable(false);
            self.isactive = ko.observable(false);

            self.parse(options.source);

            self.iconclass = ko.computed(function() {
                return self.datatypelookup[self.datatype()];
            });

            self.json = ko.computed(function() {
                return JSON.stringify(_.extend(JSON.parse(self._node()), {
                    name: self.name(),
                    datatype: self.datatype(),
                    nodegroup_id: self.nodeGroupId(),
                    cardinality: self.cardinality(),
                    validations: self.validations(),
                    isresource: self.isresource(),
                    isactive: self.isactive()
                }))
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._node();
            });

            self.isCollector = ko.computed(function () {
                return self.nodeid === self.nodeGroupId();
            });
        },

        parse: function(source) {
            var self = this;
            self._node(JSON.stringify(source));
            self.name(source.name);
            self.nodeGroupId(source.nodegroup_id);
            self.datatype(source.datatype);
            self.cardinality(source.cardinality);
            self.validations.removeAll();
            source.validations.forEach(function(validation) {
                self.validations.push(validation);
            });
            self.isresource(source.isresource);
            self.isactive(source.isactive);

            self.nodeid = source.nodeid;

            self.istopnode = source.istopnode;
            self.ontologyclass = source.ontologyclass;

            self.set('id', self.nodeid);
        },

        reset: function () {
            this.parse(JSON.parse(this._node()), self);
        },

        toJSON: function () {
            return JSON.parse(this.json());
        },

        toggleIsCollector: function () {
            var nodeGroupId = this.nodeid;
            if (this.isCollector()) {
                var _node = JSON.parse(this._node());
                nodeGroupId = (this.nodeid === _node.nodegroup_id) ? null : _node.nodegroup_id;
            }
            this.nodeGroupId(nodeGroupId);
        },

        toggleCardinality: function () {
            var cardinality = (this.cardinality()==='n')?'1':'n';
            this.cardinality(cardinality);
        }
    });
});
