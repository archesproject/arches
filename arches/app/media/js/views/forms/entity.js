define([
    'require',
    'jquery', 
    'backbone', 
    'knockout', 
    'knockout-mapping', 
    'underscore',
    'views/forms/entity-list'
], function (require, $, Backbone, ko, koMapping, _, EntityList) {
    var Entity = Backbone.View.extend({
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
            _.extend(this, koMapping.fromJS(options.data));
            this.domains = ko.toJS(options.data.domains || options.domains)

            if (this.entitytypeid in this.single_instance_entities){
                this.editing = ko.observable(true);
            }else{
                this.editing = ko.observable(options.data.editing || false);
            }

            this.child_entities.removeAll();
            _.each(this.data.child_entities, function(entity){
                this.child_entities.push(new Entity({
                    data: entity,
                    parent: this,
                    domains: this.domains,
                    single_instance_entities: this.single_instance_entities
                }));
            }, this);

            _.find(this.defaults, function(value, key){
                if (key === this.entitytypeid) {
                    //this.addDefaultEntity(key, value);
                    return true;
                }
            }, this);
            //this.addDefaultEntity(this.dataKey, ''); 

            if(options.el){
                ko.applyBindings(this, this.el);
            }
        },

        getDefaultEntity: function(entitytypeid, value){
            var entity = _.find(this.defaults, function(entity){
                if (entity.entitytypeid === entitytypeid){
                    return entity;
                }
            }, this);

            if (entity === undefined){
                entity = {
                    editing: false,
                    property: '',
                    entitytypeid: entitytypeid,
                    entityid: '',
                    value: value || '',
                    label: '',
                    businesstablename: '',
                    child_entities: []
                };
            }

            return entity;
        },

        getByTypeID: function(entitytypeid, options){
            var entities = ko.observableArray();
            if (options === undefined){
                options = {};
            }
            _.each(this.child_entities(), function (entity) {
                if (options.edited === undefined) {
                    if (entity.entitytypeid() === entitytypeid){
                        entities.push(entity);
                    }
                } else {
                    if (entity.entitytypeid() === entitytypeid && entity.editing() === options.edited){
                        entities.push(entity);
                    }
                }
            });

            if (options.edited && entities().length === 0){
                var entity = this.getDefaultEntity(entitytypeid);
                entity.editing = true;
                this.child_entities.push(new Entity({
                    data: entity,
                    parent: this,
                    single_instance_entities: this.single_instance_entities
                }));
                entities.push(koMapping.fromJS(entity));
            }
            
            return entities;
        },

        getEditedNode: function(entitytypeid, key){
            //this.addDefaultNode(entitytypeid, '');
            return ko.pureComputed({
                read: function() {
                    var ret = null;
                    // _.each(this.viewModel.branch_lists(), function(list){
                    //     if(list.editing()){
                    //         _.each(list.nodes(), function(node){
                    //             if (entitytypeid.search(node.entitytypeid()) > -1){
                    //                 ret = node[key]();
                    //             }
                    //         }, this);
                    //         if(ret === null){
                    //             _.each(this.defaults, function(node){
                    //                 if (node.entitytypeid === entitytypeid){
                    //                     list.nodes.push(koMapping.fromJS(node)); 
                    //                 }
                    //             }, this);
                    //         }
                    //     }
                    // }, this);
                    // return ret


                    var entities = this.getByTypeID(entitytypeid, {editing: true})
                    _.each(entities(), function(entity){
                        ret = entity[key]();
                    }, this);

                    return ret;

                },
                write: function(value){
                    // _.each(this.viewModel.branch_lists(), function(list){
                    //     if(list.editing()){
                    //         _.each(list.nodes(), function(node){
                    //             if (entitytypeid.search(node.entitytypeid()) > -1){
                    //                 if(typeof value === 'string'){
                    //                     node[key](value);
                    //                 }else{
                    //                     _.each(value, function(val, k, list){
                    //                         node[k](val);
                    //                     }, this);
                    //                 }
                    //             }
                    //         }, this);
                    //     }
                    // }, this);

                    var entities = this.getByTypeID(entitytypeid, {editing: true})
                    _.each(entities(), function(entity){
                        if(typeof value === 'string'){
                            entity[key](value);
                        }else{
                            _.each(value, function(val, k, list){
                                entity[k](val);
                            }, this);
                        }
                    }, this);
                },
                owner: this
            }).extend({rateLimit: 50});
        },

        getEdited: function(){
            var ret = null;
            _.each(this.entities(), function(entity){
                if(entity.editing()){
                    ret = entity;
                }
            }, this);
            return ret;
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
            var data = {
                property: this.property ? this.property : '',
                entitytypeid: this.entitytypeid ? this.entitytypeid : '',
                entityid: this.entityid ? this.entityid : '',
                value: this.value ? this.value : '',
                label: this.label ? this.label : '',
                businesstablename: this.businesstablename ? this.businesstablename : '',
                child_entities: []
            }

            _.each(this.child_entities(), function(entity){
                data.child_entities.push(entity.getData());
            }, this);

            return koMapping.toJS(data);
        },

        undoAllEdits: function(){
            this.editing(false);
            this.property ? this.property(this.data.property) : null;
            this.entitytypeid ? this.entitytypeid(this.data.entitytypeid) : null;
            this.entityid ? this.entityid(this.data.entityid) : null;
            this.value ? this.value(this.data.value) : null;
            this.label ? this.label(this.data.label) : null;
            this.businesstablename ? this.businesstablename(this.data.businesstablename) : null;

            var forremoval = _.filter(this.child_entities(), function(entity){
                if (entity.entityid() === ''){
                    return true;
                }
            }, this);

            _.each(forremoval, function(entity){
                this.child_entities.remove(entity);
            }, this);

            _.each(this.child_entities(), function(entity){
                entity.undoAllEdits();
            }, this);

            // this.addBlankEditBranch()
        }
    });

    return Entity;
});