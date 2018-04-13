define([
    'jquery',
    'knockout'
], function($, ko) {
    ko.bindingHandlers.resizableSidepanel = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var $el = $(element);
            var dragStart;
            var currentWidth;
            var dragging;
            var handle = $(document.createElement('div'))
                .addClass('sidepanel-handle')
                .attr('draggable', 'true');
            var draggable = $(document.createElement('div'))
                .addClass('sidepanel-draggable')
                .append(handle)
                .on('dragstart', function(e) {
                    dragging = true;
                    dragStart = e.pageX;
                    currentWidth = $el.width();
                })
                .on('dragend', function(e) {
                    dragging = false;
                });

            for (var i = 0; i < 3; i++) {
                handle.append(
                    $(document.createElement('i'))
                        .addClass('fa fa-circle')
                )
            }

            $el.after(draggable);
            $el.css('flex', '0 0 ' + $el.width() + 'px');
            $el.css('width', 'auto');

            document.addEventListener('dragover', function(e){
                if (dragging) {
                    e = e || window.event;
                    var dragX = e.pageX;
                    var dragY = e.pageY;
                    var width = dragStart - dragX;
                    $el.css('flex', '0 0 ' + (currentWidth - width) + 'px');
                }
            }, false);
        }
    }

    return ko.bindingHandlers.resizableSidepanel;
});
