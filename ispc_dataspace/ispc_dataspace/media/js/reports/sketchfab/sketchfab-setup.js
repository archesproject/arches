define([
    'module',
    'arches',
    'jquery',
    'utils/get-query-string-parameter'
], function (module, arches, $, getQueryStringParameter) {

    let currentUrl = module.uri;
    urlWithoutQueryString = currentUrl.split(/[?#]/)[0];
    urlWithoutFilename = urlWithoutQueryString.substr(0, urlWithoutQueryString.lastIndexOf('/'))

    var fullscreenImageOff = arches.urls.media + 'img/fullscreen_off_white.svg';
    var fullscreenImageOn = arches.urls.media + 'img/fullscreen_on_white.svg';

    function toggleFullscreen() {
        $('#sketchfab-render-area').toggleClass('fullscreen');
        $('#fullscreen-button').toggleClass('fullscreen');
        $('#sketchfab-container').toggleClass('fullscreen');
        
        let button = $('#fullscreen-button');
        if (button.attr('src').indexOf('fullscreen_off_white.svg') != -1) {
            button.attr('src', fullscreenImageOn);
        }
        else {
            button.attr('src', fullscreenImageOff) 
        }
    }

    return {
        setupSketchfab: function (embedUrl) {

            $('#fullscreen-button').click(toggleFullscreen);

            let sketchfabRenderArea = $('#sketchfab-render-area');
            sketchfabRenderArea.attr('src', embedUrl);

            // Run in fullscreen if requested through query string
            let fullscreenBool = getQueryStringParameter('fullscreen');
            if (fullscreenBool){
                if (fullscreenBool.toLowerCase() === "true"){
                    toggleFullscreen();
                }
            }
        }
    }

});