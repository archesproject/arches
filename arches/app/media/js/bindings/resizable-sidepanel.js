define([
    'jquery',
    'knockout'
], function($, ko) {
    ko.bindingHandlers.resizableSidepanel = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var draggable = $(document.createElement('div'))
                .addClass('sidepanel-draggable')
                .append(
                    $(document.createElement('div'))
                        .addClass('sidepanel-handle')
                        .append(
                            $(document.createElement('img'))
                                .attr('src', '/media/img/grab-handle.png')
                        )
                );
            var $el = $(element);

            $el.after(draggable);

            var dragStart = 0;
            var currentWidth = $el.width();
            $el.css('width', 'auto');
            $el.css('flex', '0 0 ' + currentWidth + 'px');

            draggable.on('dragstart', function(e) {
                dragStart = e.pageX;
                currentWidth = $el.width();
            });
            document.addEventListener('dragover', function(e){
                e = e || window.event;
                var dragX = e.pageX;
                var dragY = e.pageY;
                var width = dragStart - dragX;
                $el.css('flex', '0 0 ' + (currentWidth - width + 15) + 'px');
            }, false);
        }
    }

    return ko.bindingHandlers.resizableSidepanel;
});
