define(['jquery', 'backbone', 'knockout', 'knockout-mapping', 'underscore'], function ($, Backbone, ko, koMapping, _) {
    return Backbone.View.extend({

        events: {
            'click .add-button': 'addItem',
            'click [name="discard-edit-link"]': 'undoCurrentEdit'
        },

        initialize: function(options) {
            _.extend(this, options);
            this.defaults = [];
            this.viewModel = this.data[this.dataKey];
            this.branch_lists = ko.observableArray();

            // if this is a function then it's assumed to be an observableArray already
            if(typeof this.viewModel !== 'function'){
                _.each(this.viewModel.branch_lists, function(item){
                    this.branch_lists.push({
                        'editing': ko.observable(false),
                        'nodes': koMapping.fromJS(item.nodes)
                    })
                }, this);      

                _.each(this.viewModel.defaults, function(value, key){
                    this.addDefaultNode(key, value);
                }, this);   
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

        getEditedNode: function(entitytypeid, key){
            this.addDefaultNode(entitytypeid, '');
            return ko.pureComputed({
                read: function() {
                    var ret = null;
                    _.each(this.branch_lists(), function(list){
                        if(list.editing()){
                            _.each(list.nodes(), function(node){
                                if (entitytypeid.search(node.entitytypeid()) > -1){
                                    ret = node[key]();
                                }
                            }, this);
                        }
                    }, this);
                    return ret
                },
                write: function(value){
                    _.each(this.branch_lists(), function(list){
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
            _.each(this.branch_lists(), function(list){
                if(!list.editing()){
                    branch_lists.push(list);
                }
            }, this);
            return branch_lists;
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
                var editedBranch = this.getEditedBranch();
                if(editedBranch){
                    editedBranch.nodes.push(koMapping.fromJS(def));
                }else{
                    this.branch_lists.push(koMapping.fromJS({'editing':ko.observable(true), 'nodes': ko.observableArray([koMapping.fromJS(def)])})); 
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
            this.branch_lists.remove(branch);
        },

        editItem: function(branch, e) {        
            this.originalItem = koMapping.toJS(branch);
            this.removeEditedBranch();
            branch.editing(true);
            
            this.trigger('change', 'edit', branch);
        },

        getEditedBranch: function(){
            var branch = null;
            _.each(this.branch_lists(), function(list){
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
            this.branch_lists.push(branch); 
            return branch;
        },

        removeEditedBranch: function(){
            var branch = this.getEditedBranch();
            this.branch_lists.remove(branch); 
            return branch;
        },

        undoCurrentEdit: function(e) {
            this.removeEditedBranch();
            this.addBlankEditBranch();
            if(this.originalItem !== null){
                this.branch_lists.push({
                    'editing': ko.observable(false),
                    'nodes': koMapping.fromJS(this.originalItem.nodes)
                });

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
            this.branch_lists.removeAll();
            _.each(this.viewModel.branch_lists, function(item){
                this.branch_lists.push({
                    'editing': ko.observable(false),
                    'nodes': koMapping.fromJS(item.nodes)
                })
            }, this); 

            this.addBlankEditBranch()
        }
    });
});