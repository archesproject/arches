define([
    'jquery',
    'knockout',
    'chosen'
], function ($, ko) {
    ko.bindingHandlers.chosen = {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
            var $element = $(element);
            var options = ko.unwrap(valueAccessor());
            
            if (typeof options === 'object')
                $element.chosen(options);
            else
                $element.chosen();
                    
            ['options', 'selectedOptions', 'value'].forEach(function(propName){
                if (allBindings.has(propName)){
                    var prop = allBindings.get(propName);
                    if (ko.isObservable(prop)){
                        prop.subscribe(function(){
                            $element.trigger('chosen:updated');
                        });
                    }
                }
            });        
        }
    }

    return ko.bindingHandlers.chosen;
});
