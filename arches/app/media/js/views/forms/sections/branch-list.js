define(['jquery', 'backbone', 'knockout', 'knockout-mapping', 'underscore'], function ($, Backbone, ko, koMapping, _) {
    return Backbone.View.extend({

        events: {
            'click .add-button': 'addItem',
            'click .arches-CRUD-delete ': 'deleteItem',
            'click .arches-CRUD-edit ': 'editItem',
            'click [name="discard-edit-link"]': 'discardEdit'
        },

        initialize: function(options) {
            _.extend(this, options);
            this.editedItem = ko.observableArray();
            this.defaults = [];
            this.viewModel = this.data[this.dataKey];

            // if this is a function then it's assumed to be an observableArray already
            if(typeof this.viewModel !== 'function'){
                _.each(this.viewModel.defaults, function(value, key){
                    this.addDefaultNode(key, value);
                }, this);   

                this.branch_lists = koMapping.fromJS(this.viewModel.branch_lists)

                if(this.alwaysEdit && this.branch_lists().length === 1){
                    this.editedItem.removeAll();
                    _.each(this.branch_lists()[0].nodes(), function(node){
                        this.editedItem.push(node);
                    }, this);   
                }             
            }

            ko.applyBindings(this, this.el);
        },

        validateBranch: function (data) {
            return true;
        },

        validateHasValues: function(nodes){
            var valid = true;
            _.each(nodes, function (node) {
                if (node.entityid === '' && node.value === ''){
                    valid = false;
                }
            }, this);
            return valid;
        },

        getEdited: function(entitytypeid, key){
            if(!this.alwaysEdit){
                this.addDefaultNode(entitytypeid, '');
            }
            return ko.pureComputed({
                read: function() {
                    var ret = null;
                    _.each(this.editedItem(), function(node){
                        if (entitytypeid.search(node.entitytypeid()) > -1){
                            ret = node[key]();
                        }
                    }, this);
                    return ret
                },
                write: function(value){
                    _.each(this.editedItem(), function(node){
                        if (entitytypeid.search(node.entitytypeid()) > -1){
                            if(typeof value === 'string'){
                                node[key](value);
                            }else{
                                _.each(value, function(val, k, list){
                                    node[k](val);
                                }, this);
                            }
                        }
                    }, this);
                },
                owner: this
            });
        },

        addDefaultNode: function(entitytypeid, value){
            var alreadyHasDefault = false;
            var def = {
                property: '',
                entitytypeid: entitytypeid,
                entityid: '',
                value: value,
                label: '',
                businesstablename: '',
                child_entities: []
            };
            _.each(this.defaults, function(node){
                if (node.entitytypeid === entitytypeid){
                    alreadyHasDefault = true;
                }
            }, this);

            if (!alreadyHasDefault){
                this.defaults.push(def);  
                this.editedItem.push(koMapping.fromJS(def));            
            }

            return def
        },

        // onSelect2Selecting: function(item, select2Config){
        //     _.each(this.editedItem(), function(node){
        //         if (node.entitytypeid() === select2Config.dataKey){
        //             node.label(item.value);
        //             node.value(item.id);
        //             node.entitytypeid(item.entitytypeid);
        //         }
        //     }, this);
        // },

        addItem: function() {
            var data = ko.toJS(this.editedItem);
            var validationAlert = this.$el.find('.branch-invalid-alert');
            
            if (this.validateBranch(data)) {
                var all = this.editedItem.removeAll();
                this.branch_lists.push({
                    'nodes': koMapping.fromJS(all)
                });
                _.each(this.defaults, function(node){
                    this.editedItem.push(koMapping.fromJS(node));
                }, this);

                this.originalItem = null;

                this.trigger('change', 'add', data);
            } else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        },

        deleteItem: function(e) {
            var item = $(e.target).data();
            var branch = this.branch_lists()[item.index];
            this.trigger('change', 'delete', branch);   
            this.branch_lists.remove(this.branch_lists()[item.index]);
        },

        editItem: function(e) {
            var item = $(e.target).closest('.arches-CRUD-edit').data();
            var branch = this.branch_lists.splice(item.index, 1)[0];
            this.editedItem.removeAll()
            this.originalItem = koMapping.toJS(branch);
            _.each(branch.nodes(), function(node){
                this.editedItem.push(node);
            }, this);   
            
            this.trigger('change', 'edit', this.editedItem);
        },

        discardEdit: function(e) {
            if(this.originalItem !== null){
                this.branch_lists.push({
                    'nodes': koMapping.fromJS(this.originalItem.nodes)
                });
                _.each(this.defaults, function(node){
                    this.editedItem.push(koMapping.fromJS(node));
                }, this);

                this.originalItem = null;           
            }
        },

        getBranchListData: function(){
            if(this.alwaysEdit){
                return koMapping.toJS(this.branch_lists);
            }else{
                return koMapping.toJS(this.branch_lists);
            }
        },

        undoEdits: function(){
            if(this.alwaysEdit && this.data[this.dataKey].branch_lists.length === 1){
                this.editedItem.removeAll();
                _.each(this.data[this.dataKey].branch_lists[0].nodes, function(node){
                    this.editedItem.push(koMapping.fromJS(node));
                }, this);   
            }else{
                this.branch_lists.removeAll();
                _.each(this.data[this.dataKey].branch_lists, function(node){
                    this.branch_lists.push(koMapping.fromJS(node));
                }, this);

                this.editedItem.removeAll();
                _.each(this.defaults, function(node){
                    this.editedItem.push(koMapping.fromJS(node));
                }, this);
            }
        }
    });
});