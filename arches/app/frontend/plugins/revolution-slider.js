var RevolutionSlider = function() {

  return {

    //Revolution Slider - Full Screen
    initRSfullScreen: function() {
      var revapi;
      jQuery(document).ready(function() {
        revapi = jQuery('.fullscreenbanner').revolution(
          {
            delay: 5000,
            startwidth: 1170,
            startheight: 500,
            hideThumbs: 10,
            fullWidth: "on",
            fullScreen: "on",
            hideCaptionAtLimit: "",
            navigationStyle: "preview4",
            fullScreenOffsetContainer: ""
          });
      });
    }

  };
}();
