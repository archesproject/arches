define(['jquery', 
    'backbone', 
    'knockout', 
    'knockout-mapping', 
    'underscore',], function ($, Backbone, ko, koMapping, _) {
    var EntityGraph = Backbone.View.extend({

        events: {
            'click .add-button': 'addItem',
            'click [name="discard-edit-link"]': 'undoCurrentEdit'
        },


// [{
//     "label": "", 
//     "value": "", 
//     "entitytypeid": "PHASE_TYPE_ASSIGNMENT.E17", 
//     "entityid": "5ef2c5e3-0fd4-465f-9d0c-1b810e14a6ac", 
//     "property": "-P41", 
//     "businesstablename": "",
//     "child_entities": [
//         {
//             "child_entities": [], 
//             "label": "Institutional-Social Clubs/Meeting Halls", 
//             "value": "8e63c835-7b99-439c-bfb1-0dad16c4ba8a", 
//             "entitytypeid": "HERITAGE_RESOURCE_TYPE.E55", 
//             "entityid": "1c256484-e241-4a54-aff4-f36b9ccf085d", 
//             "property": "P42", 
//             "businesstablename": "domains"
//         }, 
//         {
//             "child_entities": [
//                 {
//                     "child_entities": [], 
//                     "label": "2015-03-03T00:00:00", 
//                     "value": "2015-03-03T00:00:00", 
//                     "entitytypeid": "TO_DATE.E49", 
//                     "entityid": "01d2242f-8c22-406c-b3c0-3af530cf6fc2", 
//                     "property": "P78", 
//                     "businesstablename": "dates"
//                 }, 
//                 {
//                     "child_entities": [], 
//                     "label": "2015-03-03T00:00:00", 
//                     "value": "2015-03-03T00:00:00", 
//                     "entitytypeid": "FROM_DATE.E49", 
//                     "entityid": "084e2faf-a7ca-4bf0-af8a-817885292c70", 
//                     "property": "P78", 
//                     "businesstablename": "dates"
//                 }
//             ], 
//             "label": "", 
//             "value": "", 
//             "entitytypeid": "TIME-SPAN_PHASE.E52", 
//             "entityid": "bc1d4022-5602-44ec-9fa9-3ce8986973a1", 
//             "property": "P4", 
//             "businesstablename": ""
//         }, 
//         {
//             "child_entities": [], 
//             "label": "Current", 
//             "value": "c2a89817-87ac-4794-a662-d8743170b71e", 
//             "entitytypeid": "HERITAGE_RESOURCE_USE_TYPE.E55", 
//             "entityid": "ea1119e7-fa41-44fa-97de-f7f6d93a9333", 
//             "property": "P42", 
//             "businesstablename": "domains"
//         }
//     ]
// }....]


        initialize: function(options) {
            _.extend(this, options);
            this.defaults = [];
            // this.viewModel = this.data[this.dataKey];
            // this.entities = koMapping.fromJS(this.data[this.dataKey].child_entities); 
            this.entities = koMapping.fromJS(this.data.child_entities);
            

            //if(options.el){
                _.each(this.entities(), function(item){
                    item.editing = ko.observable(false);
                }, this);      
            //}

            _.each(this.defaults, function(value, key){
                this.addDefaultEntity(key, value);
            }, this);  

            this.addDefaultEntity(this.dataKey, ''); 

            if(options.el){
                ko.applyBindings(this, this.el);
            }
        },

        // createSubBranch: function(BranchList, options){
        //     options.isSubBranch = true;
        //     options.viewModel = this.data[this.dataKey];
        //     _.each(this.entities(), function(item){
        //         if(!(options.dataKey in item)){
        //             item[options.dataKey] = ko.observableArray();
        //             options.viewModel.branch_lists = item[options.dataKey];
        //         }
        //     }, this); 
        //     return new BranchList(options);
        // },

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

        getEditedGraph: function(entitytypeid){
            this.addDefaultEntity(entitytypeid, '');
            var ret = null;
            _.each(this.entities(), function(entity){
                if(entity.editing()){
                    ret = entity;
                    // if(ret === null){
                    //     _.each(this.defaults, function(node){
                    //         if (node.entitytypeid === entitytypeid){
                    //             list.nodes.push(koMapping.fromJS(node)); 
                    //         }
                    //     }, this);
                    // }
                }


            }, this);
            if(ret === null){
                _.each(this.defaults, function(node){
                    if (node.entitytypeid === entitytypeid){
                        list.nodes.push(koMapping.fromJS(node)); 
                    }
                }, this);
            }
            return new EntityGraph({
                //el: $el,
                data: ret,
                dataKey: entitytypeid,
                validateBranch: function (data) {
                    var valid = true;
                    return valid;
                }
            });
        },

        getGraphs: function(entitytypeid){
            var ret = [];
            _.each(this.entities(), function(entity){
                if(!entity.editing() && entity.entitytypeid() === entitytypeid){
                    ret.push(entity);
                }
            }, this);
            
            return new EntityGraph({
                //el: $el,
                data: {'child_entities': ret},
                dataKey: entitytypeid,
                validateBranch: function (data) {
                    var valid = true;
                    return valid;
                }
            });
        },

        getChildGraphs: function(entitytypeid){
            var ret = [];
            _.each(this.entities(), function(entity){
                if(!entity.editing()){
                    _.each(entity.child_entities(), function(child){
                        if(child.entitytypeid() === entitytypeid){
                            ret.push(child);
                        }
                    }, this);
                }
            }, this);
            
            return new EntityGraph({
                //el: $el,
                data: {'child_entities': ret},
                dataKey: entitytypeid,
                validateBranch: function (data) {
                    var valid = true;
                    return valid;
                }
            });
        },

        getEntities: function(entitytypeid){
            var ret = [];
            _.each(this.entities(), function(entity){
                if(!entity.editing() && entity.entitytypeid() === entitytypeid){
                    ret.push(entity);
                }
            }, this);
            return ret;
        },

        // getEditedEntity: function(entitytypeid, key){
        //     this.addDefaultEntity(entitytypeid, '');
        //     return ko.pureComputed({
        //         read: function() {
        //             var ret = null;
        //             _.each(this.entities(), function(list){
        //                 if(list.editing()){
        //                     _.each(list.nodes(), function(node){
        //                         if (entitytypeid.search(node.entitytypeid()) > -1){
        //                             if(key){
        //                                 ret = node[key]();
        //                             }else{
        //                                 ret = node;
        //                             }
                                    
        //                         }
        //                     }, this);
        //                     if(ret === null){
        //                         _.each(this.defaults, function(node){
        //                             if (node.entitytypeid === entitytypeid){
        //                                 list.nodes.push(koMapping.fromJS(node)); 
        //                             }
        //                         }, this);
        //                     }
        //                 }
        //             }, this);
        //             return ret
        //         },
        //         write: function(value){
        //             _.each(this.entities(), function(list){
        //                 if(list.editing()){
        //                     _.each(list.nodes(), function(node){
        //                         if (entitytypeid.search(node.entitytypeid()) > -1){
        //                             if(typeof value === 'string'){
        //                                 node[key](value);
        //                             }else{
        //                                 _.each(value, function(val, k, list){
        //                                     node[k](val);
        //                                 }, this);
        //                             }
        //                         }
        //                     }, this);
        //                 }
        //             }, this);
        //         },
        //         owner: this
        //     }).extend({rateLimit: 50});
        // },

        getBranchLists: function() {
            var branch_lists = [];
            _.each(this.entities(), function(list){
                if(!list.editing()){
                    branch_lists.push(list);
                }
            }, this);
            return branch_lists;
        },

        addDefaultEntity: function(entitytypeid, value){
            return ;
            var alreadyHasDefault = false;
            var def = {
                editing: false,
                property: '',
                entitytypeid: entitytypeid,
                entityid: '',
                value: value,
                label: '',
                businesstablename: '',
                child_entities: []
            };
            _.each(this.defaults, function(entity){
                if (entity.entitytypeid === entitytypeid){
                    alreadyHasDefault = true;
                }
            }, this);

            if (!alreadyHasDefault){
                this.defaults.push(def); 
                var editedBranch = this.getEditedBranch();
                if(editedBranch){
                    editedBranch.child_entities.push(koMapping.fromJS(def));
                }else{
                    def.editing = ko.observable(true);
                    this.entities.push(koMapping.fromJS(def)); 
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
            this.entities.remove(branch);
        },

        editItem: function(branch, e) {        
            this.originalItem = koMapping.toJS(branch);
            this.removeEditedBranch();
            branch.editing(true);
            
            this.trigger('change', 'edit', branch);
        },

        getEditedBranch: function(){
            var ret = null;
            _.each(this.entities(), function(entity){
                if(entity.editing()){
                    ret = entity;
                }
            }, this);
            return ret;
        },

        addBlankEditBranch: function(){
          var branch = koMapping.fromJS({
                'editing':ko.observable(true), 
                'nodes': ko.observableArray(this.defaults)
            });
            this.entities.push(branch); 
            return branch;
        },

        removeEditedBranch: function(){
            var branch = this.getEditedBranch();
            this.entities.remove(branch); 
            return branch;
        },

        undoCurrentEdit: function(e) {
            this.removeEditedBranch();
            this.addBlankEditBranch();
            if(this.originalItem !== null){
                this.entities.push({
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
            this.entities.removeAll();
            _.each(this.data[this.dataKey], function(item){
                this.entities.push({
                    'editing': ko.observable(false),
                    'nodes': koMapping.fromJS(item.nodes)
                })
            }, this); 

            this.addBlankEditBranch()
        }
    });

    return EntityGraph;
});