define(['jquery', 'backbone', 'knockout', 'underscore', 'plugins/knockout-select2', 'plugins/knockout-summernote'], function ($, Backbone, ko, _) {
    return Backbone.View.extend({
        
        // events: function(){
        //     return {
        //         'click #saveedits': 'submit',
        //         'click #canceledits': 'cancel'
        //     }
        // },

        constructor: function (options) {
            var self = this;
            this.branchLists = [];

            ko.observableArray.fn.get = function(entitytypeid, key) {
                var allItems = this();
                var ret = '';
                _.each(allItems, function(node){
                    if (entitytypeid.search(node.entitytypeid()) > -1){
                        ret = node[key]();
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
            $("#end-workflow").click(function(){
                self.startWorkflow();
                self.saveWizard(); 
                return false; 
            });
            $("#cancel-workflow").click(function(){ 
                self.startWorkflow(); 
                return false; 
            });

        },

        startWorkflow: function() {    
            $( ["#workflow-container", "#current-items"].join(",") ).toggle(300);
            $( ["#cancel-workflow","#end-workflow","#start-workflow"].join(",")  ).toggle();
        },

        saveWizard: function() {    
            $( ["#completed-evaluations"].join(",")  ).toggle(300);
            $( ["#related-files"].join(",")  ).css("display", "block");
            $( ["#no-evaluations", "#no-files"].join(",")  ).css("display", "none");
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
            return true;
        },

        submit: function(){
            if (this.validate()){
                this.form.find('#formdata').val(this.getData());
                this.form.submit(); 
            }
        },

        cancel: function(){
            _.each(this.branchLists, function(branchList){
                branchList.undoAllEdits();
            }, this);  
        }
    });
});