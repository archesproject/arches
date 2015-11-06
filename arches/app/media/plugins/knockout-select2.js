
define(['jquery', 'knockout', 'underscore', 'select2'], function ($, ko, _) {
    ko.bindingHandlers.select2 = {
        init: function(el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            var self = this;
            var data;
            var domains = {};
            var allBindings = allBindingsAccessor();
            var branchList = bindingContext.$data;
            var select2Config = ko.utils.unwrapObservable(allBindings.select2);            

            ko.utils.domNodeDisposal.addDisposeCallback(el, function() {
                $(el).select2('destroy');
            });

            select2Config.formatResult = function (item) {
                return item.text;
            };

            domains[select2Config.dataKey] = [];
            domains = select2Config.domains || branchList.domains || (branchList.viewModel ? branchList.viewModel.domains : undefined) || domains;
            select2Config.data = domains[select2Config.dataKey];

            _.each(select2Config.data, function (item) {
                if (item.collector === 'collector') {
                    delete item.id;
                }
            });

            select2Config.createSearchChoice = function(term, data) { 
                if ($(data).filter(function() 
                    { return this.text.localeCompare(term)===0; }).length===0) {
                        return {id:term, text:term};
                    }
                }

            select2Config.getConceptPath = function(root_conceptid) {
                var root = {'children': select2Config.data}
                var result = [];
                var isParent = false;
  
                function lookForChild(obj, conceptid) {
                    isParent = false;
                    _.each(obj.children, function (item) {
                        if (item.conceptid === conceptid) {
                            isParent = true;
                            result.push(obj)
                        } 
                    });

                    if (isParent === false) {
                        for (var i=0; i<obj.children.length;i+=1){
                            lookForChild(obj.children[i], conceptid);
                        }
                    } else {
                        lookForChild(root, obj.conceptid);
                    }
                };

                lookForChild(root, root_conceptid)

                return result;
            }

            select2Config.formatSelection = function (item) {
                var path = [];
                var result = item.text;
                if (select2Config.showParents === true) {
                    path = this.getConceptPath(item.conceptid);
                    if (path.length > 1) {
                        result = path[0].text + ": " + item.text;
                    }
                }
                return result
            };


            $(el).select2(select2Config);


            $(el).on("change", function(val) {
                // $(".select2-container .select2-choice").css({ "height": "200px;" }); Trying to change height of select2 result container to show more parents
                if(val.added){
                    return select2Config.value({'value':val.added.id, 'label':val.added.text, 'entitytypeid': val.added.entitytypeid});
                }
                return select2Config.value(val.val);
            });
        },

        update: function (el, valueAccessor, allBindingsAccessor, viewmodel, bindingContext) {
            // we don't want the setting of the select2 dropdown value (eg: $(el).select2("val", val.value, true) ) 
            // to re-trigger the element binding (in this case it's usually a getEditedNode call on the dropdown
            // because that can have the side affect of adding a new blank node) so we use ko.ignoreDependencies
            var val = '';
            if(valueAccessor().value){
                val = ko.utils.unwrapObservable(valueAccessor().value());
                if (typeof val === 'string' || val === null){
                    return ko.ignoreDependencies($(el).select2, $(el) , ["val", val, true]);
                }
                if (typeof val === 'object'){
                    return ko.ignoreDependencies($(el).select2, $(el) , ["val", val.value, true]);
                }
            }else{
                return ko.ignoreDependencies($(el).select2, $(el) , ["val", val, true]);
            }
        }
    };

    return ko.bindingHandlers.select2;
});