import $ from 'jquery';
import _ from 'underscore';
import ko from 'knockout';
import arches from 'arches';
import 'chosen';


/**
* A knockout.js binding for the "chosen.js" select box - https://harvesthq.github.io/chosen/
* - pass options to chosen using the following syntax in the knockout data-bind attribute
* @example
* chosen: {disable_search_threshold: 10, width: '100%', ....}"
* @constructor
* @name chosen
*/
ko.bindingHandlers.chosen = {
    init: function(element, valueAccessor, allBindings, viewModel, bindingContext){
        var $element = $(element);
        var options = ko.unwrap(valueAccessor());
        var defaults = {
            search_contains: true,
            rtl: arches.activeLanguageDir == "rtl"
        };
        
        if (options.disabled === true) {
            $element.attr('disabled', true);
        }

        if (allBindings.has('placeholder')){
            var prop = allBindings.get('placeholder');
            var value = prop;
            if (ko.isObservable(prop)){
                prop.subscribe(function(){
                    $element.attr('data-placeholder', prop());
                    $element.trigger('chosen:updated');
                });
                value = prop();
            }
            $element.attr('data-placeholder', value);
        }

        if (typeof options === 'object')
            $element.chosen(_.defaults(options, defaults));
        else
            $element.chosen(defaults);

        ['options', 'selectedOptions', 'value'].forEach(function(propName){
            if (allBindings.has(propName)){
                var prop = allBindings.get(propName);
                if (ko.isObservable(prop) || ko.isComputed(prop)){
                    prop.subscribe(function(){
                        $element.trigger('chosen:updated');
                    });
                }
            }
        });
    }
};
ko.bindingHandlers.chosen.init = ko.bindingHandlers.chosen.init.bind(ko.bindingHandlers.chosen);

export default ko.bindingHandlers.chosen;
