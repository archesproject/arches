define([
    'knockout',
    'arches',
    'utils/resource',
    'viewmodels/resource-instance-select',
    'bindings/select2-query'
], function(ko, arches, ResourceUtils, ResourceInstanceSelectViewModel) {
    return ko.components.register('views/components/resource-instance-nodevalue', {
        viewModel: function(params) {
            const self = this;
            let relatedResourceNodeValues;

            ResourceInstanceSelectViewModel.apply(this, [params]);

            this.relatedResourceId = params.relatedResourceId;
            this.relatedNodeId = params.relatedNodeId;

            this.lookupResourceInstanceData(self.relatedResourceId).then( data => {
                relatedResourceNodeValues = ResourceUtils.getNodeValues({
                    nodeId: self.relatedNodeId,
                }, data._source.tiles).map(rr => rr.resourceId);
            });

            this.select2Config = {
                value: self.renderContext === 'search' ? self.value : self.resourceToAdd,
                clickBubble: true,
                disabled: self.disabled,
                multiple: !self.displayOntologyTable ? self.multiple : false,
                placeholder: this.placeholder() || arches.translations.riSelectPlaceholder,
                closeOnSelect: true,
                allowClear: self.renderContext === 'search' ? true : false,
                onSelect: function(item) {
                    self.selectedItem(item);
                    if (self.renderContext !== 'search') {
                        var ret = self.makeObject(item.resourceinstanceid, item);
                        self.setValue(ret);
                        window.setTimeout(function() {
                            if(self.displayOntologyTable){
                                self.resourceToAdd("");
                            }
                        }, 250);
                    }    
                },
                ajax: {
                    url: arches.urls.related_resources + self.relatedResourceId + "?paginate=false",
                    dataType: 'json',
                    results: function(data) {
                        const filteredResources = data.related_resources.filter(resource => relatedResourceNodeValues.includes(resource.resourceinstanceid));
                        return {
                            results: filteredResources,
                        };
                    }
                },
                id: function(item) {
                    return item.resourceinstanceid;
                },
                formatResult: function(item) {
                    if (item.displayname) {
                        return item.displayname;
                    }
                },
                formatSelection: function(item) {
                    if (item.displayname) {
                        return item.displayname;
                    }
                },
                initSelection: function(ele, callback) {
                    if(self.renderContext === "search" && self.value() !== "") {
                        var values = self.value();
                        if(!Array.isArray(self.value())){
                            values = [self.value()];
                        }
        
                        var lookups = [];
        
                        values.forEach(function(val){
                            var resourceId;
                            if (typeof val === 'string') {
                                resourceId = val;
                            }
                            else if (ko.unwrap(val.resourceId)) {
                                resourceId = ko.unwrap(val.resourceId);
                            }
        
                            var resourceInstance = self.lookupResourceInstanceData(resourceId).then(
                                function(resourceInstance) { return resourceInstance; }
                            );
                
                            if (resourceInstance) { lookups.push(resourceInstance); }
                        });
        
                        Promise.all(lookups).then(function(arr){
                            if (arr.length) {
                                let ret = arr.map(function(item) {
                                    return {"displayname": item["_source"].displayname, "resourceinstanceid": item["_id"]};
                                });
                                if(self.multiple === false) {
                                    ret = ret[0];
                                }
                                callback(ret);
                            }
                        });
                    }
                }
            };
        },
        template: {
            require: 'text!widget-templates/resource-instance-select'
        }
    });
});
