define(['jquery', 'backbone', 'knockout', 'knockout-mapping', 'underscore'], function ($, Backbone, ko, koMapping, _) {
    return Backbone.View.extend({
        viewModel: null,
        key: '',
        pkField: '',

        events: {
            'click .add-button': 'addItem',
            'click .arches-CRUD-delete ': 'deleteItem',
            'click .arches-CRUD-edit ': 'editItem'
        },

        initialize: function(options) {
            _.extend(this, _.pick(options, 'viewModel', 'key', 'pkField'));

            this.viewModel[this.key] = ko.observableArray(this.viewModel[this.key]);
            this.viewModel.editing[this.key] = koMapping.fromJS(this.viewModel.defaults[this.key]);
        },

        addItem: function() {
            var data = ko.toJS(this.viewModel.editing[this.key]),
                defaults = this.viewModel.defaults[this.key];
            if (!data[this.pkField] && !data.__tempId__) {
                data.__tempId__ = _.uniqueId('tempId_');
            }
            delete data.__ko_mapping__;
            this.viewModel[this.key].push(data);
            defaults.__tempId__ = '';
            koMapping.fromJS(defaults, this.viewModel.editing[this.key]);
        },

        matchItem: function(item, data) {
            matchField = this.pkField;
            if (!data[matchField.toLowerCase()]) {
                matchField = '__tempId__';
            }
            return item[matchField] === data[matchField.toLowerCase()];
        },

        deleteItem: function(e) {
            var self = this,
                data = $(e.target).data();

            this.viewModel[this.key].remove(function(item) {
                return self.matchItem(item, data);
            });
        },

        editItem: function(e) {
            var self = this,
                data = $(e.target).closest('.arches-CRUD-edit').data();

            this.viewModel[this.key].remove(function(item) {
                var match = self.matchItem(item, data);
                if (match) {
                    koMapping.fromJS(ko.toJS(item), self.viewModel.editing[self.key]);
                }
                return match;
            });
        }
    });
});