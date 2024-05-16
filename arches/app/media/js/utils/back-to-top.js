define([], function(){

    let backToTop = {
        scrollToTopHandler: function() {
            // Get the button:
            let mybutton = document.getElementById("backToTopBtn");
            
            // When the user scrolls down 200px from the top of the document, show the button
            window.onscroll = function() {scrollFunction();};
            function scrollFunction() {
                if (document.body.scrollTop > 200 || document.documentElement.scrollTop > 200) {
                    mybutton.style.opacity = "0.5";
                } else {
                    mybutton.style.opacity = "0";
                }
            }
        },

        // When the user clicks on the button, scroll to the top of the document
        backToTopHandler: function() {
            document.body.scrollTop = 0; // For Safari
            document.documentElement.scrollTop = 0; // For Chrome, Firefox, IE and Opera
        },
    };

    return backToTop;
});
