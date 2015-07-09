define(['jquery', 'backbone', 'knockout', 'underscore', 'plugins/knockout-select2', 'plugins/knockout-summernote'], function ($, Backbone, ko, _) {
    return Backbone.View.extend({
        
        events: {
            'click .confirm-delete-yes': 'delete'
        },

        constructor: function (options) {
            var self = this;
            this.branchLists = [];

            ko.observableArray.fn.get = function(entitytypeid, key) {
                var allItems = this();
                var ret = '';
                _.filter(allItems, function(node){
                    if ('entitytypeid' in node && entitytypeid.search(node.entitytypeid()) > -1){
                        if(key){
                            ret = node[key]();
                        }else{
                            ret = node;
                        }
                        return true;
                    }
                }, this);
                return ret
            }

            Backbone.View.apply(this, arguments);
            
            return this;
        },

        initialize: function() {
            var self = this;
            this.form = this.$el;
            // parse then restringify JSON data to ensure whitespace is identical
            this._rawdata = ko.toJSON(JSON.parse(this.form.find('#formdata').val()));
            this.data = JSON.parse(this._rawdata);

            //Show and hide Upload Wizard.  
            $("#start-workflow").click(function(){ 
                self.startWorkflow();
                return false; 
            });
            $("#end-workflow").click(function(evt){
                self.submit(evt); 
                return false; 
            });
            $("#cancel-workflow").click(function(){ 
                self.cancleWorkflow();
                return false; 
            });
            this.$el.find('.form-load-mask').hide();
        },

        toggleEditor: function() { 
            var branchLists = this.branchLists;   
            var formLoaded = function() {
                _.each(branchLists, function(branchList) {
                    branchList.trigger('formloaded');
                })
            }
            $( ["#workflow-container", "#current-items"].join(",") ).toggle(300, formLoaded);
            $( ["#cancel-workflow","#end-workflow","#start-workflow"].join(",")  ).toggle();
        },

        startWorkflow: function() { 
            this.toggleEditor(); 
        },

        cancleWorkflow: function() { 
            this.toggleEditor(); 
        },

        addBranchList: function(branchList){
            var self = this;
            this.branchLists.push(branchList);
            this.listenTo(branchList, 'change', function(eventtype, item){
                self.trigger('change', eventtype, item);                 
            });
            return branchList;
        },

        getData: function(includeDomains){
            var data = {};
            _.each(this.branchLists, function(branchList){
                data[branchList.dataKey] = branchList.getData();
            }, this);  
            return ko.toJSON(data);
        },

        validate: function(){
            var isValid = true
            _.each(this.branchLists, function(branchList){
                isValid = isValid && branchList.validate();
            }, this); 
            return isValid;
        },

        submit: function(evt){
            var validationAlert = this.$el.find('.branch-invalid-alert');;
            evt.preventDefault();

            if (this.validate()){
                this.$el.find('.form-load-mask').show();
                this.form.find('#formdata').val(this.getData());
                this.form.submit(); 
            }else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        },

        delete: function(){
            var nodes = [];
            var data = {};
            _.each(this.deleted_assessment, function(value, key, list){
                data[key] = [];
                _.each(value.branch_lists, function(branch_list){
                    nodes = []
                    _.each(branch_list.nodes, function(node){
                           node.value = '';
                           nodes.push(node);
                        }, this);
                    data[key].push({'nodes': nodes});
                }, this);
            }, this);
            this.form.find('#formdata').val(ko.toJSON(data));
            this.form.submit(); 
        },

        cancel: function(){
            _.each(this.branchLists, function(branchList){
                branchList.undoAllEdits();
            }, this);  
        },

        isDirty: function () {
            return false;
        }
    });
});