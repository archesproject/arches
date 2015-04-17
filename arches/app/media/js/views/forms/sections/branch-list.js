define(['jquery', 
    'backbone', 
    'knockout', 
    'knockout-mapping', 
    'underscore',], function ($, Backbone, ko, koMapping, _) {
    return Backbone.View.extend({

        events: {
            'click .add-button': 'addItem',
            'click [name="discard-edit-link"]': 'undoCurrentEdit'
        },

        initialize: function(options) {
            var self = this;
            this.singleEdit = false;

            _.extend(this, options);

            this.defaults = [];
            this.viewModel = JSON.parse(JSON.stringify(this.data[this.dataKey]));
            //this.viewModel.domains = this.data[this.dataKey].domains;
            this.viewModel.branch_lists = koMapping.fromJS(this.data[this.dataKey].branch_lists);

            // if this is a function then it's assumed to be an observableArray already
            if(typeof this.viewModel !== 'function'){
                _.each(this.viewModel.branch_lists(), function(item){
                    item.editing = ko.observable(false);
                }, this);      

                _.each(this.viewModel.defaults, function(value, entitytypeid){
                    this.addDefaultNode(entitytypeid, 'value', value);
                }, this);   
            }

            ko.applyBindings(this, this.el);

            if (this.singleEdit) {
                _.each(this.viewModel.branch_lists(), function (branch) {
                    if (branch) {
                        _.each(branch.nodes(), function (node) {
                            var value = node.value();
                            if (value) {
                                this.editItem(branch);
                            }
                        }, this);
                    }
                }, this);

                var editingBranch = this.getEditedBranch();
                _.each(editingBranch.nodes(), function (node) {
                    node.value.subscribe(function () {
                        self.trigger('change', 'edit', editingBranch);
                    });
                });
            }
        },

        validate: function(){
            var valid = true;
            _.each(this.viewModel.branch_lists(), function(list){
                if (this.singleEdit || !list.editing()){
                    valid = valid && this.validateBranch(ko.toJS(list.nodes));
                }
            }, this); 
            return valid;
        },

        validateBranch: function (data) {
            return true;
        },

        validateHasValues: function(nodes){
            var valid = nodes != undefined && nodes.length > 0;
            _.each(nodes, function (node) {
                if (node.entityid === '' && node.value === ''){
                    valid = false;
                }
            }, this);
            return valid;
        },

        getEditedNode: function(entitytypeid, key){
            this.addDefaultNode(entitytypeid, key, '');
            return ko.pureComputed({
                read: function() {
                    var ret = null;
                    _.each(this.viewModel.branch_lists(), function(list){
                        if(list.editing()){
                            _.each(list.nodes(), function(node){
                                if (entitytypeid.search(node.entitytypeid()) > -1){
                                    ret = node[key]();
                                }
                            }, this);
                            if(ret === null){
                                _.each(this.defaults, function(node){
                                    if (node.entitytypeid === entitytypeid){
                                        list.nodes.push(koMapping.fromJS(node)); 
                                    }
                                }, this);
                            }
                        }
                    }, this);
                    return ret
                },
                write: function(value){
                    _.each(this.viewModel.branch_lists(), function(list){
                        if(list.editing()){
                            _.each(list.nodes(), function(node){
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
                        }
                    }, this);
                },
                owner: this
            }).extend({rateLimit: 50});
        },

        getBranchLists: function() {
            var branch_lists = [];
            _.each(this.viewModel.branch_lists(), function(list){
                if(!list.editing() || (this.singleEdit && list.editing())){
                    branch_lists.push(list);
                }
            }, this);
            return branch_lists;
        },

        addDefaultNode: function(entitytypeid, key, value){
            var alreadyHasDefault = false;
            var def = {
                property: '',
                entitytypeid: entitytypeid,
                entityid: '',
                value: '',
                label: '',
                businesstablename: '',
                child_entities: []
            };
            def[key] = value;
            _.each(this.defaults, function(node){
                if (node.entitytypeid === entitytypeid){
                    alreadyHasDefault = true;
                }
            }, this);

            if (!alreadyHasDefault){
                this.defaults.push(def); 
                var editedBranch = this.getEditedBranch();
                if(editedBranch){
                    editedBranch.nodes.push(koMapping.fromJS(def));
                }else{
                    this.viewModel.branch_lists.push(koMapping.fromJS({'editing':ko.observable(true), 'nodes': ko.observableArray([koMapping.fromJS(def)])})); 
                }     
            }

            return def
        },

        addItem: function() {
            var branch = this.getEditedBranch();
            var validationAlert = this.$el.find('.branch-invalid-alert');
            
            if (this.validateBranch(ko.toJS(branch.nodes))) {
                var branch = this.getEditedBranch();
                branch.editing(false);
                this.addBlankEditBranch();
                this.originalItem = null;

                this.trigger('change', 'add', branch);
            } else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        },

        deleteItem: function(branch, e) {
            this.trigger('change', 'delete', branch);   
            this.viewModel.branch_lists.remove(branch);
        },

        editItem: function(branch, e) {        
            this.originalItem = koMapping.toJS(branch);
            this.removeEditedBranch();
            branch.editing(true);
            
            this.trigger('change', 'edit', branch);
        },

        getEditedBranch: function(){
            var branch = null;
            _.each(this.viewModel.branch_lists(), function(list){
                if(list.editing()){
                    branch = list;
                }
            }, this);
            return branch;
        },

        addBlankEditBranch: function(){
          var branch = koMapping.fromJS({
                'editing':ko.observable(true), 
                'nodes': ko.observableArray(this.defaults)
            });
            this.viewModel.branch_lists.push(branch); 
            return branch;
        },

        removeEditedBranch: function(){
            var branch = this.getEditedBranch();
            this.viewModel.branch_lists.remove(branch); 
            return branch;
        },

        undoCurrentEdit: function() {
            this.removeEditedBranch();
            this.addBlankEditBranch();
            if(this.originalItem !== null){
                this.viewModel.branch_lists.push(koMapping.fromJS(_.extend({editing: false}, this.originalItem)));

                this.originalItem = null;  
            }         
        },

        getData: function(){
            var data = koMapping.toJS(this.getBranchLists());
            _.each(data, function(item){
                var i = item;
                delete item.editing;
            }, this); 
            return data
        },

        undoAllEdits: function(){
            this.viewModel.branch_lists.removeAll();
            _.each(this.data[this.dataKey].branch_lists, function(item){
                this.viewModel.branch_lists.push(koMapping.fromJS(_.extend({editing: this.singleEdit}, item)));
            }, this); 

            if(!this.singleEdit || this.viewModel.branch_lists().length === 0){
                this.addBlankEditBranch();
            }
        }
    });
});