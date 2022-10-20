define([
    'jquery',
    'underscore',
    'knockout'
], function ($, _, ko) {
    /**
    * A knockout.js binding for the "ckeditor" rich text editor widget
    * - pass options to ckeditor using the following syntax in the knockout
    * data-bind attribute
    * @example
    * ckeditor: {height: 250}
    * @constructor
    * @name ckeditor
    */

    const initialize = function (element, valueAccessor, allBindings) {
        var modelValue = valueAccessor();
        var value = ko.utils.unwrapObservable(valueAccessor());
        var $element = $(element);
        var options = {};

        if (allBindings.has('ckeditorOptions')){
            var opts = allBindings.get('ckeditorOptions');
            options = (typeof opts === 'object') ? opts : {};
        };

        // Set initial value and create the CKEditor
        $element.html(value);
        var editor = $element.ckeditor(options).editor;

        allBindings()?.attr?.disabled?.subscribe(disabled => {
            if(!!editor?.editable() && (disabled === true || disabled === false)) {
                editor?.setReadOnly(disabled);
            }
        });


        // bind to change events and link it to the observable
        var onChange = function (e) {
            var self = this;

            if (ko.isWriteableObservable(self)) {
                var newValue = $(e.listenerData).val();
                if (!((self() === null || self() === "") && (newValue === null || newValue === ""))) {
                    self(newValue);
                }
            }
            return true;
        };
        editor.on('change', onChange, modelValue, element);

        modelValue.subscribe(function(newValue){
            var self = this;
            var $element = $(element);
            var newValue = ko.utils.unwrapObservable(valueAccessor());
            if (editor.getData() != newValue) {
                // remove the listener and then add back to prevent `setData`
                // from triggering the onChange event
                editor.removeListener('change', onChange );
                editor.setData(newValue);
                editor.on('change', onChange, modelValue, element);
            }
        }, this)


        // Handle disposal if KO removes an editor through template binding
        ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
            editor.updateElement();
            editor.destroy();
        });
    };

    ko.bindingHandlers.ckeditor = {
        init: (element, valueAccessor, allBindings) => {
            require(['ckeditor-jquery', 'ckeditor'], () => {
                initialize(element, valueAccessor, allBindings);
            })
        }
    };

    return ko.bindingHandlers.ckeditor;
});
