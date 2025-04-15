import $ from 'jquery';
import ko from 'knockout';

// eslint-disable-next-line no-undef
(function(e,t){var n=function(e,t,n){var r;return function(){function u(){if(!n)e.apply(s,o);r=null;}var s=this,o=arguments;if(r)clearTimeout(r);else if(n)e.apply(s,o);r=setTimeout(u,t||100);};};jQuery.fn[t]=function(e){return e?this.bind("resize",n(e)):this.trigger(t);};})(jQuery,"smartresize");

ko.bindingHandlers.smartresize = {
    init: function(element, valueAccessor, allBindings, viewModel) {
        var options = ko.unwrap(valueAccessor());
        var childclass = options.childclass;
        function update_grid() {
            var content_width = $(element).width()+20;
            const images_per_row = Math.floor(content_width / 300);
            var width = Math.round(content_width / images_per_row);
            var height = Math.round(width/3*1.8);
            $(element).find(childclass).each(function(id){
                var x = Math.round((id % images_per_row) * width);
                var y = Math.floor(id/images_per_row) * height + Math.floor(id/images_per_row) * 20;
                if (navigator.appName.indexOf("Internet Explorer")!=-1){
                    $(this).animate({width: width-3+'px', height: height+'px', left: x, top: y},600);
                } else {
                    $(this).css({'width': width-3+'px', 'height': height+'px', 'left': x, 'top': y });
                }
            });

            if (images_per_row == 1) {
                // console.log(images_per_row)
            }
        }
        $(window).smartresize(update_grid);
        $(window).ready(update_grid);
    }
};
ko.bindingHandlers.smartresize.init = ko.bindingHandlers.smartresize.init.bind(ko.bindingHandlers.smartresize);

export default ko.bindingHandlers.smartresize;
