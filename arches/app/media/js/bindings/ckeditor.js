define([
    'jquery',
    'underscore',
    'knockout',
    'ckeditor-jquery',
    'ckeditor',
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
    ko.bindingHandlers.ckeditor = {
        init: function (element, valueAccessor, allBindings, viewModel, bindingContext) {
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
        }
    };

    return ko.bindingHandlers.ckeditor;
});
