define([
    'jquery', 
    'backbone', 
    'knockout', 
    'knockout-mapping', 
    'underscore'
], function ($, Backbone, ko, koMapping, _) {



    
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
            _.extend(this, koMapping.fromJS(this.data));

            this.editing = ko.observable(false);

            this.child_entities = new EntityList({
                //el: this.el,
                data: this.data.child_entities,
                defaults: this.defaults
            });

            _.find(this.defaults, function(value, key){
                if(key === this.entitytypeid){
                    //this.addDefaultEntity(key, value);
                    return true;
                }
            }, this);
            //this.addDefaultEntity(this.dataKey, ''); 

            if(options.el){
                ko.applyBindings(this, this.el);
            }
        },

        addDefaultEntity: function(entitytypeid, value){
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
            var data = koMapping.toJS({
                editing: this.editing,
                property: this.property,
                entitytypeid: this.entitytypeid,
                entityid: this.entityid,
                value: this.value,
                label: this.label,
                businesstablename: this.businesstablename,
                child_entities: this.child_entities.getData()
            });
            return data
        }
    });


    var EntityList = Backbone.View.extend({
        
        initialize: function(options) {
            this.entities = ko.observableArray();
            this.data = [];
            this.defaults = {};

            _.extend(this, options);

            _.each(this.data, function (entityData) {
                this.entities.push(
                    new Entity({
                        //el: this.el,
                        data: entityData,
                        defaults: this.defaults
                    })
                );
            }, this);

            if(options.el){
                ko.applyBindings(this, this.el);
            }
        },

        getByTypeID: function (entitytypeid, edited) {
            var entities = [];
            _.each(this.entities(), function (entity) {
                if (edited === undefined) {
                    if (entity.entitytypeid() === entitytypeid){
                        entities.push(entity.getData());
                    }
                } else {
                    if (entity.entitytypeid() === entitytypeid && entity.editing() === edited){
                        entities.push(entity.getData());
                    }
                }
            });
            return new EntityList({
                data: entities
            });
        },

        applyEdits: function() {
            var entity = this.getEditedEntity();
            var validationAlert = this.$el.find('.branch-invalid-alert');
            
            if (this.isValid()) {
                _.each(this.entities(), function(entity) {
                    if (entity.editing()) {
                        entity.editing(false);
                        this.entities.push(
                            new Entity({
                                entitytypeid: entity.entitytypeid(),
                                editing: true,
                                defaults: defaults
                            })
                        );
                    }
                });

                this.trigger('change', 'add', entity);
            } else {
                validationAlert.show(300);
                setTimeout(function() {
                    validationAlert.fadeOut();
                }, 5000);
            }
        },

        isValid: function () {
            return true;
        },

        revert: function(e) {
            _.each(this.entities, function(entity) {
                if (entity.entityid()) {
                    entity.revert()
                    this.entities.push(entity);
                }
            });
        },

        deleteItem: function(item, e) {
            this.entities.remove(item);
            this.trigger('change', 'delete', item);
        },

        editItem: function(entity, e) {        
            this.originalItem = koMapping.toJS(entity);
            this.removeEditedEntity();
            entity.editing(true);
            
            this.trigger('change', 'edit', entity);
        },

        getEditedEntity: function(){
            var ret = null;
            _.each(this.entities(), function(entity){
                if(entity.editing()){
                    ret = entity;
                }
            }, this);
            return ret;
        },

        addBlankEditEntity: function(){
            var entity = koMapping.fromJS({
                'editing':ko.observable(true), 
                'nodes': ko.observableArray(this.defaults)
            });
            this.entities.push(entity); 
            return entity;
        },

        removeEditedEntity: function(){
            var entity = this.getEditedEntity();
            this.entities.remove(entity); 
            return entity;
        },

        undoCurrentEdit: function(e) {
            this.removeEditedEntity();
            this.addBlankEditEntity();
            if(this.originalItem !== null){
                this.entities.push({
                    'editing': ko.observable(false),
                    'nodes': koMapping.fromJS(this.originalItem.nodes)
                });

                this.originalItem = null;  
            }         
        },

        getData: function(){
            var data = [];
            _.each(this.entities(), function(entity){
                data.push(entity.getData());
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

            this.addBlankEditEntity()
        }
    });

    return EntityList;
});