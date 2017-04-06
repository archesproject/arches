define([
    'jquery',
    'underscore',
    'knockout',
    'ckeditor-jquery',
    'ckeditor',
], function ($, _, ko) {
    /**
    * A knockout.js binding for the "summernote" rich text editor widget
    * - pass options to summernote using the following syntax in the knockout
    * data-bind attribute
    * @example
    * summernote: {height: 250}
    * @constructor
    * @name summernote
    */
    ko.bindingHandlers.ckeditor = {
        init: function (element, valueAccessor) {
 
            var modelValue = valueAccessor();
            var value = ko.utils.unwrapObservable(valueAccessor());
            var $element = $(element);
            var changedByUI = false;
            var setByData = false
     
            // Set initial value and create the CKEditor
            $element.html(value);
            var editor = $element.ckeditor().editor;
     
            // bind to change events and link it to the observable
            var onChange = function (e) {
                var self = this;

                if (!setByData && ko.isWriteableObservable(self)) {
                    changedByUI = true;
                    var newValue = $(e.listenerData).val();
                    if (!((self() === null || self() === "") && (newValue === null || newValue === ""))) {
                        self(newValue);
                    }
                    changedByUI = false;
                }
                return true;
            };
            editor.on('change', onChange, modelValue, element);

            modelValue.subscribe(function(newValue){
                var self = this;
                var $element = $(element);
                var newValue = ko.utils.unwrapObservable(valueAccessor());
                if (!changedByUI && $element.ckeditorGet().getData() != newValue) {
                    setByData = true;
                    if (newValue === null){
                        editor.removeListener( 'change', onChange );
                    }
                    $element.ckeditorGet().setData(newValue);
                    if (newValue === null){
                       editor.on('change', onChange, modelValue, element);
                    }
                    setByData = false;
                }
            }, this)
     
     
            /* Handle disposal if KO removes an editor 
             * through template binding */
            ko.utils.domNodeDisposal.addDisposeCallback(element, 
                function () {
                    editor.updateElement();
                    editor.destroy();
                });
        },
 
        /* Hook and handle the binding updating so we write 
         * back to the observable */
        update: function (element, valueAccessor) {
            // var self = this;
            // var $element = $(element);
            // var newValue = ko.utils.unwrapObservable(valueAccessor());
            // if ($element.ckeditorGet().getData() != newValue) {
            //     $element.ckeditorGet().setData(newValue);
            // }
        }
    };

    return ko.bindingHandlers.ckeditor;
});
