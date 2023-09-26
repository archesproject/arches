define([
    'jquery',
    'knockout'
], function($, ko) {
    const initialize = function(element, valueAccessor, CodeMirror) {
        var options = ko.toJS(valueAccessor());
        options.value = options.value || '';
        var editor = new CodeMirror(element, options);
        editor.on('change', function(cm) {
            var value = ko.unwrap(valueAccessor()).value;
            if (ko.isObservable(value)) {
                value(cm.getValue());
            } else {
                ko.unwrap(valueAccessor()).value = cm.getValue();
            }
        });
        var subscriptions = [];
        if (ko.isObservable(valueAccessor().value)) {
            subscriptions.push(valueAccessor().value.subscribe(function() {
                if (editor.getValue() !== valueAccessor().value())
                    editor.setValue(valueAccessor().value());
            }));
        }
        if (ko.isObservable(valueAccessor().mode)) {
            subscriptions.push(valueAccessor().mode.subscribe(function() {
                editor.setOption('mode', valueAccessor().mode());
            }));
        }

        var wrapperElement = $(editor.getWrapperElement());
        ko.utils.domNodeDisposal.addDisposeCallback(element, function() {
            wrapperElement.remove();
            for (var i = 0; i < subscriptions.length; i++) {
                subscriptions[i].dispose();
            }
        });
    };

    ko.bindingHandlers.codemirror = {
        init: (element, valueAccessor) => {
            require(['codemirror','codemirror/mode/javascript/javascript'], (codemirror) => {
                initialize(element, valueAccessor, codemirror);
            });
        }
    };

    return ko.bindingHandlers.codemirror;
});
