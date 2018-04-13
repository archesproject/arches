define([
    'jquery',
    'knockout'
], function($, ko) {
    ko.bindingHandlers.resizableSidepanel = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var $el = $(element);
            var dragStart;
            var currentWidth;
            var handle = $(document.createElement('div'))
                .addClass('sidepanel-handle')
                .attr('draggable', 'true');
            var draggable = $(document.createElement('div'))
                .addClass('sidepanel-draggable')
                .append(handle);

            for (var i = 0; i < 3; i++) {
                handle.append(
                    $(document.createElement('i'))
                    .addClass('fa fa-circle')
                )
            }

            $el.after(draggable);
            $el.css('flex', '0 0 ' + $el.width() + 'px');
            $el.css('width', 'auto');

            draggable.on('dragstart', function(e) {
                dragStart = e.pageX;
                currentWidth = $el.width();
            });

            document.addEventListener('dragover', function(e){
                e = e || window.event;
                var dragX = e.pageX;
                var dragY = e.pageY;
                var width = dragStart - dragX;
                $el.css('flex', '0 0 ' + (currentWidth - width) + 'px');
            }, false);
        }
    }

    return ko.bindingHandlers.resizableSidepanel;
});
