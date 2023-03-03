define([
    'jquery',
    'knockout',
    'arches'
], function($, ko, arches) {
    ko.bindingHandlers.resizableSidepanel = {
        init: function(element, valueAccessor, allBindings, viewModel) {
            var $el = $(element);
            var start = null;
            var handle = $(document.createElement('div'))
                .attr('draggable', 'true');

            for (var i = 0; i < 3; i++) {
                handle.append(
                    $(document.createElement('i')).addClass('fa fa-circle')
                );
            }

            $el.after(
                $(document.createElement('div'))
                    .addClass('sidepanel-draggable')
                    .append(handle)
                    .on('dragstart', function(e) {
                        if(arches.activeLanguageDir == "rtl"){
                            start = $el.width() + e.pageX;
                        } else {
                            start = $el.width() - e.pageX;
                        }
                        // Fix for Firefox where dragging was not working:
                        e.originalEvent.dataTransfer.setData('Text', this.id);
                    })
                    .on('dragend', function(e) {
                        start = null;
                    })
            );

            if(arches.activeLanguageDir == "rtl"){
                $el.css('flex', $el.width() + 'px 0 0');
            } else {

                $el.css('flex', '0 0 ' + $el.width() + 'px');
            }
            $el.css('width', 'auto');

            document.addEventListener('dragover', function(e){
                if (start !== null) {
                    if(arches.activeLanguageDir == "rtl"){
                        $el.css('flex', (start - e.pageX) + 'px 0 0');
                    } else {
                        $el.css('flex',  '0 0 ' + (start + e.pageX) + 'px');
                    }
                }
            }, false);
        }
    };

    return ko.bindingHandlers.resizableSidepanel;
});
