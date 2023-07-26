define(['jquery'], function($){

    var ariaUtils = {
        toggleAriaExpanded: function(id) {
            const ele = document.getElementById(id);
            let x = ele.getAttribute("aria-expanded"); 
            if (x === "true") {
                x = "false";
            } else {
                x = "true";
            }
            ele.setAttribute("aria-expanded", x);
        },

        handleEscKey: function(toggleElement, listenerScope) {
            /* 
            *   toggleElement: element that expands/contracts a panel, menu, etc. 
            *   listenerScope: when focus is within this element, an escape key press will close the element controled by toggleElement
            * 
            *   Implement this function within the toggleElement's click event handler, passing event.currentTarget as toggleElement
            */
            let attachListener = function(evt) {
                evt = evt || window.event;
                var isEscape = false;
                
                // Check for escape key press
                if ('key' in evt) {
                    isEscape = (evt.key === 'Escape' || evt.key === 'Esc');
                } else {
                    isEscape = (evt.keyCode === 27);
                }

                // Handle escape key press
                if (isEscape) {
                    $(toggleElement).click();
                    $(toggleElement).focus();
                    $(listenerScope).off('keydown', attachListener);
                }
            };
            $(listenerScope).on('keydown', attachListener);
            $(listenerScope).find('button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])').eq(0).focus();
        },

        shiftFocus: function(focusTarget) {
            /* 
            *   focusTarget: element to which focus will be moved. Should have tabindex="-1" or 0 and an aria-label
            */
            $(focusTarget).focus();
        },
    };

    return ariaUtils;
});
