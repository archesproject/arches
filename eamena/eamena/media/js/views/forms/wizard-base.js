define(['jquery', 'backbone', 'knockout', 'underscore', 'plugins/knockout-select2', 'plugins/knockout-summernote'], function ($, Backbone, ko, _) {
    return Backbone.View.extend({
        
        events: {
            'click .confirm-delete-yes': 'delete',
            'click .edit-actor': 'toggleEditActor'
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
                self.cancelWorkflow();
                return false; 
            });
            this.on('change', function(eventtype, item){
                $('#cancel-workflow').removeClass('disabled');
                $('#remove-workflow').removeClass('disabled');
                $('#end-workflow').removeClass('disabled');
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

        cancelWorkflow: function() { 
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

        // this fails if any branchlists that have been marked
        // requiredBranch == true are empty, both of new or existing nodes
        validate: function(current_data){
            var isValid = true
            _.some(this.branchLists, function(branchList){
                if (branchList.requiredBranch == true) {
                    if (current_data[branchList.dataKey].length == 0) {
                        if (branchList['data'][branchList.dataKey]['branch_lists'].length == 0) {
                            isValid = false;
                            return
                        }
                    }
                }
            }, this);
            return isValid;
        },

        submit: function(evt){
            var validationAlert = this.$el.find('.wizard-invalid-alert');
            evt.preventDefault();

            if (this.validate(JSON.parse(this.getData()))){
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
        },
        
        toggleEditActor: function (e) {
            var actorClass = e.target.dataset.actor;
            if ($(e.target).hasClass("show-box")) {
                $(".show-box." + actorClass).addClass('hidden');
                $(".hide-box." + actorClass).removeClass('hidden');
                $(".edit-actors-row." + actorClass).removeClass('hidden');
            } else {
                $(".show-box." + actorClass).removeClass('hidden');
                $(".hide-box." + actorClass).addClass('hidden');
                $(".edit-actors-row." + actorClass).addClass('hidden');
            }
        },

    });
});