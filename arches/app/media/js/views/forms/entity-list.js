define(['jquery', 
    'backbone', 
    'knockout', 
    'knockout-mapping', 
    'underscore'
], function ($, Backbone, ko, koMapping, _) {
    var EntityList = Backbone.View.extend({
        initialize: function(options) {
            this.entities = ko.observableArray();
            this.data = [];
            this.defaults = {};

            _.extend(this, options);

            _.each(this.data, function (entityData) {
                this.entities.push(
                    new Entity({
                        data: entityData,
                        defaults: defaults
                    })
                );
            });

            if(options.el){
                ko.applyBindings(this, this.el);
            }
        },

        getByTypeID: function (entitytypeid, edited) {
            var entities = ko.observableArray();
            _.each(this.entities(), function (entity) {
                if (edited === undefined) {
                    if (entity.entitytypeid() === entitytypeid){
                        entities.push(entity);
                    }
                } else {
                    if (entity.entitytypeid() === entitytypeid && entity.editing() === edited){
                        entities.push(entity);
                    }
                }
            });
            return new EntityList({
                entities: entities
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
            var data = koMapping.toJS(this.getEntityLists());
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

            this.addBlankEditEntity()
        }
    });

    return EntityList;
});