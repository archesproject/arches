define([
    'jquery',
    'knockout'
], function($, ko) {
    ko.bindingHandlers.scrollTo = {
        update: function(element, valueAccessor, allBindings) {
            var _value = valueAccessor();
            
            if (ko.unwrap(_value)) {
                var target = $(element);
                var container = $(allBindings.get('container') || 'html, body');
                var scrollDirection = allBindings.get('scrollDirection') || 'vertical';

                if (scrollDirection === 'vertical') {
                    var top = $(window).height();
                    var containerTop = container.offset().top;
                    var bottom = target.offset().top + target.outerHeight();

                    if (bottom > top || bottom < containerTop) {
                        container.stop().animate({
                            scrollTop: target.offset().top - containerTop + container.scrollTop() - 50
                        }, 500);
                    }
                }
                else if (scrollDirection === 'horizontal') {
                    var leftScreenBoundary = 50;  /* left-nav width */
                    var rightScreenBoundary = $(window).width();

                    var targetOffsetLeft = target.offset().left;
                    var targetOffsetRight = targetOffsetLeft + target.width();

                    if (targetOffsetLeft < leftScreenBoundary) {
                        container.stop().animate({
                            scrollLeft: container.scrollLeft() + targetOffsetLeft - leftScreenBoundary
                        }, 500);

                    } 
                    else if (targetOffsetRight > rightScreenBoundary) {
                        container.stop().animate({
                            scrollLeft: container.scrollLeft() + targetOffsetRight - rightScreenBoundary
                        }, 500);
                    }
                }
            }
        }
    };

    return ko.bindingHandlers.scrollTo;
});
