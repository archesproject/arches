define([
    'underscore',
    'knockout',
    'models/abstract',
    'arches'
], function(_, ko, AbstractModel, arches) {
    return AbstractModel.extend({
        url: arches.urls.project,

        initialize: function(options) {
            var self = this;
            self.identities = options.identities || [];
            self._project = ko.observable('{}');
            self.name = ko.observable('');
            self.active = ko.observable(false);
            self.createdby = ko.observable(null);
            self.lasteditedby = ko.observable(null);
            self.users = ko.observableArray();
            self.groups = ko.observableArray();
            var getUserName = function(id) {
                var user = _.find(self.identities, function(i) {
                    return i.type === 'user' && i.id === id;
                });
                return user ? user.name : '';
            };
            self.createdbyName = ko.computed(function () {
                return getUserName(self.createdby());
            });
            self.lasteditedbyName = ko.computed(function () {
                return getUserName(self.lasteditedby());
            });

            self.parse(options.source);

            self.json = ko.computed(function() {
                var jsObj = ko.toJS({
                    name: self.name,
                    active: self.active,
                    id: self.get('id')
                })
                return JSON.stringify(_.extend(JSON.parse(self._project()), jsObj))
            });

            self.dirty = ko.computed(function() {
                return self.json() !== self._project() || !self.get('id');
            });
        },

        parse: function(source) {
            var self = this;
            self._project(JSON.stringify(source));
            self.name(source.name);
            self.active(source.active);
            self.createdby(source.createdby_id);
            self.lasteditedby(source.lasteditedby_id);
            self.groups(source.groups);
            self.users(source.users);

            self.set('id', source.id);
        },

        reset: function() {
            this.parse(JSON.parse(this._project()), self);
        },

        _getURL: function(method){
            return this.url;
        },

        save: function (userCallback, scope) {
            var self = this;
            var method = "POST";
            var callback = function (request, status, model) {
                if (typeof userCallback === 'function') {
                    userCallback.call(this, request, status, model);
                }
                if (status==='success') {
                    self.set('id', request.responseJSON.project.id);
                    self.createdby(request.responseJSON.project.createdby_id);
                    self.lasteditedby(request.responseJSON.project.lasteditedby_id);
                    self.groups(request.responseJSON.project.groups);
                    self.users(request.responseJSON.project.users);
                    this._project(this.json());
                };
            };
            this._doRequest({
                type: method,
                url: this._getURL(method),
                data: JSON.stringify(this.toJSON())
            }, callback, scope, 'save');
        },

        toJSON: function() {
            return JSON.parse(this.json());
        }
    });
});
