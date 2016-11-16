define([
    'jquery',
    'knockout',
    'jquery-ui'
], function ($, ko) {
    var _dragged;
    ko.bindingHandlers.drag = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel) {
            var dragElement = $(element);
            var dragOptions = {
                helper: 'clone',
                revert: true,
                revertDuration: 0,
                start: function() {
                    _dragged = ko.utils.unwrapObservable(valueAccessor().value);
                },
                cursor: 'default',
                scroll: false,
                zIndex: 1000,
                appendTo: 'body'
            };
            dragElement.draggable(dragOptions).disableSelection();
        }
    };

    ko.bindingHandlers.drop = {
        init: function(element, valueAccessor, allBindingsAccessor, viewModel) {
            var dropElement = $(element);
            var dropOptions = {
                drop: function(event, ui) {
                    valueAccessor().value(_dragged);
                }
            };
            dropElement.droppable(dropOptions);
        }
    };
    return;
});
