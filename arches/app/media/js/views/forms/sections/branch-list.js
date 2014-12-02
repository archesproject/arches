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
            if (this.pkField === ''){
                this.pkField = this.key + '__entityid';                
            }

            this.viewModel[this.key] = ko.observableArray(this.viewModel[this.key]);
            this.viewModel.editing[this.key] = koMapping.fromJS(this.viewModel.defaults[this.key]);
        },

        validateBranch: function (data) {
            return true;
        },

        addItem: function() {
            var data = ko.toJS(this.viewModel.editing[this.key]);
            var validationAlert = this.$el.find('.branch-invalid-alert');
            
            if (this.validateBranch(data)) {
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

        deleteItem: function(e) {
            var data = $(e.target).data();
            var item = this.viewModel[this.key]()[data.index];

            this.trigger('change', 'delete', item);   
            this.viewModel[this.key].remove(this.viewModel[this.key]()[data.index]);
        },

        editItem: function(e) {
            var data = $(e.target).closest('.arches-CRUD-edit').data();
            var item = this.viewModel[this.key]()[data.index];

            this.trigger('change', 'edit', item);
            koMapping.fromJS(ko.toJS(item), this.viewModel.editing[this.key]);
            this.viewModel[this.key].remove(item);
        }
    });
});