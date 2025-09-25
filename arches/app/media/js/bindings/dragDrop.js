import $ from 'jquery';
import ko from 'knockout';
import 'jquery-ui'; 

var _dragged;
ko.bindingHandlers.drag = {
    init: function(element, valueAccessor, allBindingsAccessor, viewModel) {
        if (!valueAccessor().preventDrag) {
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
        } else {
            console.log(valueAccessor());
        }
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
