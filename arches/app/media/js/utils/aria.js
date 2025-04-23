import $ from 'jquery';

const ariaUtils = {
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

    handleEscKey: function(openElement, escListenerScope, closeElement) {
        /* 
        *   openElement: element that expands/contracts a panel, menu, etc. 
        *   escListenerScope: when focus is within this element, an escape key press will close the element controlled by openElement
        *   closeElement: [OPTIONAL] element that closes the panel, menu, etc. when clicked - use this param when the panel is not removed from DOM on close
        * 
        *   Implement this function within the openElement's click event handler, passing event.currentTarget as openElement
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
            if (isEscape && closeElement) {
                $(closeElement).click();
                $(openElement).focus();
            } else if (isEscape) {
                $(openElement).click();
                $(openElement).focus();
            }
        };
        $(escListenerScope).off('keydown', attachListener);
        $(escListenerScope).on('keydown', attachListener);
        $(escListenerScope).find('button, a, input, select, textarea, [tabindex]:not([tabindex="-1"])').eq(0).focus();
    },

    shiftFocus: function(focusTarget) {
        /* 
        *   focusTarget: element to which focus will be moved. Should have tabindex="-1" or 0 and an aria-label
        */
        $(focusTarget).focus();
    },
};

export default ariaUtils;
