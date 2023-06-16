define([], function(){

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
        }
    };

    return ariaUtils;
});
