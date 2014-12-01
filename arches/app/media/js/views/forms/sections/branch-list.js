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
            _.extend(this, _.pick(options, 'viewModel', 'key', 'pkField', 'validateBranch'));

            _.each(this.viewModel[this.key], function (item) {
                item.tempId = '';
            });
            this.viewModel.defaults[this.key].tempId = '';

            this.viewModel[this.key] = ko.observableArray(this.viewModel[this.key]);
            this.viewModel.editing[this.key] = koMapping.fromJS(this.viewModel.defaults[this.key]);
        },

        validateBranch: function (data) {
            return true;
        },

        addItem: function() {
            var data = ko.toJS(this.viewModel.editing[this.key]),
                validationAlert = this.$el.find('.branch-invalid-alert');
            if (this.validateBranch(data)) {
                if (!data[this.pkField] && !data.tempId) {
                    data.tempId = _.uniqueId('tempId_');
                }
                delete data.__ko_mapping__;
				this.trigger('change', 'add', data);
                this.viewModel[this.key].push(data);
                koMapping.fromJS(this.viewModel.defaults[this.key], this.viewModel.editing[this.key]);
            } else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        },

        matchItem: function(item, data) {
            matchField = this.pkField;
            if (!data[matchField.toLowerCase()]) {
                matchField = 'tempId';
            }
            return item[matchField] === data[matchField.toLowerCase()];
        },

        deleteItem: function(e) {
            var self = this,
                data = $(e.target).data();

            this.viewModel[this.key].remove(function(item) {
                if(self.matchItem(item, data)){
                    self.trigger('change', 'delete', item);   
                    return true;                 
                }
                return false;
            });
        },

        editItem: function(e) {
            var self = this,
                data = $(e.target).closest('.arches-CRUD-edit').data();

            this.viewModel[this.key].remove(function(item) {
                var match = self.matchItem(item, data);
                if (match) {
                    self.trigger('change', 'edit', item);
                    koMapping.fromJS(ko.toJS(item), self.viewModel.editing[self.key]);
                }
                return match;
            });
        }
    });
});